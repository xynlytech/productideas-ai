from abc import ABC, abstractmethod
from typing import Any


class BaseSourceConnector(ABC):
    source_type: str = "unknown"

    @abstractmethod
    async def fetch(self, queries: list[str], region: str = "US") -> list[dict[str, Any]]:
        """Fetch raw signals for given queries. Returns list of signal dicts."""
        ...

    @abstractmethod
    async def health_check(self) -> dict:
        """Return source health status."""
        ...


# Registry of connectors
_connectors: dict[str, BaseSourceConnector] = {}


def register_connector(connector: BaseSourceConnector):
    _connectors[connector.source_type] = connector


def get_connector(source_type: str) -> BaseSourceConnector:
    if source_type not in _connectors:
        raise ValueError(f"Unknown source: {source_type}")
    return _connectors[source_type]


async def get_all_source_status() -> list[dict]:
    statuses = []
    for name, connector in _connectors.items():
        try:
            status = await connector.health_check()
            statuses.append({"source": name, **status})
        except Exception as e:
            statuses.append({"source": name, "healthy": False, "error": str(e)})
    return statuses
