
import hashlib
import json

from app.models.opportunity import Opportunity


class OpportunityIdentityError(ValueError):
    """Raised when an opportunity identity cannot be generated."""


class OpportunityIdentityService:
    """
    Generates deterministic identity fingerprints for opportunities.

    Identity intentionally excludes volatile fields such as:
    - database id
    - collected_at
    - updated_at
    - verification status
    - verified_at
    - existing fingerprint
    - metadata
    - source_url

    The source URL is excluded because the same opportunity may be
    discovered through multiple sources.

    Application URL is retained because it is a strong cross-source
    identity signal.
    """

    @staticmethod
    def _normalize_text(value):
        if value is None:
            return ""

        return " ".join(
            str(value).strip().casefold().split()
        )

    @staticmethod
    def _normalize_url(value):
        if value is None:
            return ""

        return (
            str(value)
            .strip()
            .rstrip("/")
            .casefold()
        )

    @classmethod
    def identity_payload(cls, opportunity: Opportunity):
        if not isinstance(opportunity, Opportunity):
            raise OpportunityIdentityError(
                "identity_payload() requires an Opportunity."
            )

        title = cls._normalize_text(
            opportunity.title
        )
        organization = cls._normalize_text(
            opportunity.organization
        )

        if not title:
            raise OpportunityIdentityError(
                "Opportunity title cannot be empty."
            )

        if not organization:
            raise OpportunityIdentityError(
                "Opportunity organization cannot be empty."
            )

        opportunity_type = (
            opportunity.opportunity_type.value
            if hasattr(
                opportunity.opportunity_type,
                "value",
            )
            else cls._normalize_text(
                opportunity.opportunity_type
            )
        )

        return {
            "title": title,
            "organization": organization,
            "opportunity_type": opportunity_type,
            "application_url": cls._normalize_url(
                opportunity.application_url
            ),
        }

    @classmethod
    def fingerprint(cls, opportunity: Opportunity):
        payload = cls.identity_payload(
            opportunity
        )

        canonical_json = json.dumps(
            payload,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        )

        return hashlib.sha256(
            canonical_json.encode("utf-8")
        ).hexdigest()
