import asyncio
import logging
from datetime import UTC, datetime
from typing import Any

import httpx

from app.services.ingestion import BaseSourceConnector, register_connector

logger = logging.getLogger(__name__)

AUTOCOMPLETE_URL = "https://suggestqueries.google.com/complete/search"


class GoogleAutocompleteConnector(BaseSourceConnector):
    source_type = "google_autocomplete"

    def __init__(self):
        self._last_fetch: datetime | None = None
        self._consecutive_errors = 0

    async def fetch(self, queries: list[str], region: str = "US") -> list[dict[str, Any]]:
        signals = []
        async with httpx.AsyncClient(timeout=15.0) as client:
            for query in queries:
                try:
                    response = await client.get(
                        AUTOCOMPLETE_URL,
                        params={
                            "client": "firefox",
                            "q": query,
                            "gl": region.lower(),
                        },
                        headers={
                            "User-Agent": "Mozilla/5.0 (compatible; ProductIdeasBot/1.0)",
                        },
                    )
                    response.raise_for_status()
                    data = response.json()

                    suggestions = data[1] if isinstance(data, list) and len(data) > 1 else []

                    signals.append({
                        "source_type": self.source_type,
                        "query": query,
                        "region": region,
                        "raw_data": {
                            "suggestions": suggestions[:20],
                            "original_query": query,
                        },
                        "status": "raw",
                        "ingested_at": datetime.now(UTC).isoformat(),
                    })
                    self._consecutive_errors = 0

                    # Rate limiting
                    await asyncio.sleep(1)

                except httpx.HTTPStatusError as e:
                    self._consecutive_errors += 1
                    logger.warning(f"Autocomplete HTTP error for '{query}': {e.response.status_code}")
                    if e.response.status_code == 429:
                        await asyncio.sleep(30)
                except Exception as e:
                    self._consecutive_errors += 1
                    logger.error(f"Autocomplete error for '{query}': {e}")

        self._last_fetch = datetime.now(UTC)
        return signals

    async def health_check(self) -> dict:
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(
                    AUTOCOMPLETE_URL,
                    params={"client": "firefox", "q": "test"},
                )
                reachable = resp.status_code < 500
        except Exception:
            reachable = False

        return {
            "healthy": reachable and self._consecutive_errors < 5,
            "reachable": reachable,
            "consecutive_errors": self._consecutive_errors,
            "last_fetch": self._last_fetch.isoformat() if self._last_fetch else None,
        }


_connector = GoogleAutocompleteConnector()
register_connector(_connector)
