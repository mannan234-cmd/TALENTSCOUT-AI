from __future__ import annotations

from typing import Dict, Iterable, List, Optional

from app.models.opportunity import OpportunitySourceType
from app.models.opportunity_source import (
    OpportunitySource,
    OpportunitySourceCreate,
    OpportunitySourceUpdate,
)


class OpportunitySourceService:
    """
    In-memory source registry/business layer.

    Database persistence will be added to the collection architecture
    once source behavior is established and tested.
    """

    def __init__(
        self,
        sources: Optional[Iterable[OpportunitySource]] = None,
    ) -> None:
        self._sources: Dict[str, OpportunitySource] = {}

        if sources:
            for source in sources:
                self.add(source)

    def add(self, source: OpportunitySource) -> OpportunitySource:
        if not source.id:
            raise ValueError("Source id is required for registry insertion.")

        if source.id in self._sources:
            raise ValueError(f"Source '{source.id}' already exists.")

        self._sources[source.id] = source
        return source

    def create(
        self,
        source_id: str,
        payload: OpportunitySourceCreate,
    ) -> OpportunitySource:
        if source_id in self._sources:
            raise ValueError(f"Source '{source_id}' already exists.")

        source = OpportunitySource(
            id=source_id,
            **payload.model_dump(mode="python"),
        )

        self._sources[source_id] = source
        return source

    def get(self, source_id: str) -> Optional[OpportunitySource]:
        return self._sources.get(source_id)

    def list(
        self,
        *,
        active_only: bool = False,
        collection_enabled_only: bool = False,
        source_type: Optional[OpportunitySourceType] = None,
    ) -> List[OpportunitySource]:
        results = list(self._sources.values())

        if active_only:
            results = [
                source for source in results
                if source.is_active
            ]

        if collection_enabled_only:
            results = [
                source for source in results
                if source.collection_enabled
            ]

        if source_type is not None:
            results = [
                source for source in results
                if source.source_type == source_type
            ]

        return sorted(
            results,
            key=lambda source: (source.priority, source.name.lower()),
        )

    def update(
        self,
        source_id: str,
        payload: OpportunitySourceUpdate,
    ) -> OpportunitySource:
        existing = self._sources.get(source_id)

        if existing is None:
            raise KeyError(f"Source '{source_id}' not found.")

        changes = payload.model_dump(
            mode="python",
            exclude_unset=True,
        )

        updated = existing.model_copy(update=changes)

        # Re-validate the complete object after update.
        updated = OpportunitySource.model_validate(
            updated.model_dump(mode="python")
        )

        self._sources[source_id] = updated
        return updated

    def deactivate(self, source_id: str) -> OpportunitySource:
        return self.update(
            source_id,
            OpportunitySourceUpdate(
                is_active=False,
                collection_enabled=False,
            ),
        )

    def activate(self, source_id: str) -> OpportunitySource:
        return self.update(
            source_id,
            OpportunitySourceUpdate(
                is_active=True,
                collection_enabled=True,
            ),
        )

    def remove(self, source_id: str) -> OpportunitySource:
        existing = self._sources.pop(source_id, None)

        if existing is None:
            raise KeyError(f"Source '{source_id}' not found.")

        return existing

    def count(self) -> int:
        return len(self._sources)
