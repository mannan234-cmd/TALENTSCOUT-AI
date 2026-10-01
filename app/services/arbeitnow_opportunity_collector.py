
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

import requests

from app.models.opportunity_collection import (
    BaseOpportunityCollector,
    CollectedOpportunity,
    CollectionResult,
)
from app.models.opportunity_source import OpportunitySource
from app.models.opportunity import OpportunitySourceType


class ArbeitnowOpportunityCollector(BaseOpportunityCollector):
    """
    Collector for the public Arbeitnow Job Board API.

    Source:
        https://www.arbeitnow.com/api/job-board-api

    This collector only transforms data returned by the real source.
    It never creates or invents opportunity content.
    """

    collector_name = "arbeitnow"

    DEFAULT_API_URL = "https://www.arbeitnow.com/api/job-board-api"
    TIMEOUT_SECONDS = 30

    def supports(self, source: OpportunitySource) -> bool:
        return (
            source.source_type == OpportunitySourceType.AGGREGATOR
            and (
                "arbeitnow.com" in str(source.base_url).lower()
                or source.name.strip().lower() == "arbeitnow"
            )
        )

    def _timestamp_to_datetime(
        self,
        value: Any,
    ) -> Optional[datetime]:
        if value is None:
            return None

        try:
            timestamp = int(value)
            return datetime.fromtimestamp(
                timestamp,
                tz=timezone.utc,
            )
        except (TypeError, ValueError, OverflowError):
            return None

    def _clean_html(self, value: Any) -> str:
        if not value:
            return ""

        text = str(value)

        import re

        text = re.sub(
            r"<br\s*/?>",
            "\n",
            text,
            flags=re.IGNORECASE,
        )

        text = re.sub(
            r"</p\s*>",
            "\n",
            text,
            flags=re.IGNORECASE,
        )

        text = re.sub(
            r"<[^>]+>",
            " ",
            text,
        )

        text = re.sub(
            r"[ \t]+",
            " ",
            text,
        )

        text = re.sub(
            r"\n\s*\n+",
            "\n\n",
            text,
        )

        return text.strip()

    def _build_opportunity(
        self,
        record: Dict[str, Any],
    ) -> CollectedOpportunity:
        title = str(record.get("title") or "").strip()
        company = str(record.get("company_name") or "").strip()
        description = self._clean_html(
            record.get("description")
        )

        tags = record.get("tags") or []
        if not isinstance(tags, list):
            tags = [str(tags)]

        job_types = record.get("job_types") or []
        if not isinstance(job_types, list):
            job_types = [str(job_types)]

        location = record.get("location")

        remote_value = record.get("remote")
        remote = (
            bool(remote_value)
            if remote_value is not None
            else None
        )

        source_url = record.get("url")

        slug = record.get("slug")

        created_at = self._timestamp_to_datetime(
            record.get("created_at")
        )

        metadata = {
            "source": "arbeitnow",
            "source_slug": slug,
            "source_record": record,
            "job_types": job_types,
        }

        return CollectedOpportunity(
            title=title,
            organization=company,
            description=description,
            location=str(location).strip()
            if location
            else None,
            remote=remote,
            opportunity_type="job",
            eligibility=[],
            requirements=[],
            skills=[str(item) for item in tags],
            benefits=[],
            application_url=source_url,
            source_url=source_url,
            source_name="Arbeitnow",
            source_type=OpportunitySourceType.AGGREGATOR,
            deadline=None,
            tags=[str(item) for item in tags],
            metadata=metadata,
            collected_at=created_at
            or datetime.now(timezone.utc),
        )

    def collect(
        self,
        source: OpportunitySource,
    ) -> CollectionResult:
        started_at = datetime.now(timezone.utc)

        try:
            api_url = str(
                source.metadata.get(
                    "api_url",
                    self.DEFAULT_API_URL,
                )
            )

            response = requests.get(
                api_url,
                timeout=self.TIMEOUT_SECONDS,
                headers={
                    "User-Agent": "TalentScout_AI/1.0"
                },
            )

            response.raise_for_status()

            payload = response.json()

            records = payload.get("data", [])

            if not isinstance(records, list):
                raise ValueError(
                    "Arbeitnow response 'data' is not a list."
                )

            opportunities: List[CollectedOpportunity] = []
            errors: List[str] = []

            for index, record in enumerate(records):
                try:
                    if not isinstance(record, dict):
                        raise ValueError(
                            "Record is not a JSON object."
                        )

                    opportunity = self._build_opportunity(record)

                    opportunities.append(opportunity)

                except Exception as exc:
                    errors.append(
                        f"record[{index}]: {exc}"
                    )

            return self.build_result(
                source=source,
                opportunities=opportunities,
                errors=errors,
                started_at=started_at,
                pages_processed=1,
                items_seen=len(records),
            )

        except Exception as exc:
            return self.build_result(
                source=source,
                opportunities=[],
                errors=[str(exc)],
                started_at=started_at,
                pages_processed=0,
                items_seen=0,
            )
