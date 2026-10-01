from __future__ import annotations

from typing import Dict, Iterable, List, Optional

from app.models.opportunity_collection import OpportunityCollector
from app.models.opportunity_source import OpportunitySource


class OpportunityCollectorRegistry:
    """
    Registry that maps opportunity sources to collector implementations.
    """

    def __init__(
        self,
        collectors: Optional[Iterable[OpportunityCollector]] = None,
    ) -> None:
        self._collectors: Dict[str, OpportunityCollector] = {}

        if collectors:
            for collector in collectors:
                self.register(collector)

    def register(
        self,
        collector: OpportunityCollector,
    ) -> OpportunityCollector:
        name = collector.collector_name.strip()

        if not name:
            raise ValueError("Collector name cannot be empty.")

        if name in self._collectors:
            raise ValueError(
                f"Collector '{name}' is already registered."
            )

        self._collectors[name] = collector
        return collector

    def get(
        self,
        collector_name: str,
    ) -> Optional[OpportunityCollector]:
        return self._collectors.get(collector_name)

    def list(self) -> List[OpportunityCollector]:
        return list(self._collectors.values())

    def find_for_source(
        self,
        source: OpportunitySource,
    ) -> Optional[OpportunityCollector]:
        for collector in self._collectors.values():
            if collector.supports(source):
                return collector

        return None

    def require_for_source(
        self,
        source: OpportunitySource,
    ) -> OpportunityCollector:
        collector = self.find_for_source(source)

        if collector is None:
            raise LookupError(
                f"No collector registered for source '{source.name}'."
            )

        return collector

    def count(self) -> int:
        return len(self._collectors)
