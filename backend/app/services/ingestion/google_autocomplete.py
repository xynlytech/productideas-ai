import asyncio
import logging
from datetime import UTC, datetime
from typing import Any

import httpx

from app.services.ingestion import BaseSourceConnector, register_connector

logger = logging.getLogger(__name__)

AUTOCOMPLETE_URL = "https://suggestqueries.google.com/complete/search"

# Seed query templates that surface real unmet demand.
# These are intentionally phrased to trigger autocomplete in "need/problem" space.
DEFAULT_SEED_QUERIES = [
    # Pain-point discovery
    "best app for",
    "tool to automate",
    "software to manage",
    "how to track",
    "i need a way to",
    "why is there no app for",
    "app to help with",
    "how do companies manage",
    # Market categories
    "ai tool for",
    "chrome extension for",
    "saas for",
    "dashboard for",
    "analytics for",
    "workflow automation for",
    "no code tool for",
    # Business segments
    "tool for freelancers",
    "software for small business",
    "app for remote teams",
    "platform for creators",
    "marketplace for",
]


class GoogleAutocompleteConnector(BaseSourceConnector):
    source_type = "google_autocomplete"

    def __init__(self):
        self._last_fetch: datetime | None = None
        self._consecutive_errors = 0

    async def fetch(self, queries: list[str], region: str = "US") -> list[dict[str, Any]]:
        """
        Fetch autocomplete suggestions for each query seed.
        Each suggestion returned by Google becomes its own independent signal —
        this is the core mechanism for surfacing unarticulated demand.
        """
        # Merge caller-supplied queries with defaults; deduplicate
        all_queries = list(dict.fromkeys(queries + DEFAULT_SEED_QUERIES))

        signals = []
        async with httpx.AsyncClient(
            timeout=15.0,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/122.0.0.0 Safari/537.36"
                ),
            },
            follow_redirects=True,
        ) as client:
            for query in all_queries:
                try:
                    response = await client.get(
                        AUTOCOMPLETE_URL,
                        params={
                            "client": "firefox",
                            "q": query,
                            "gl": region.lower(),
                            "hl": "en",
                        },
                    )
                    response.raise_for_status()
                    data = response.json()

                    suggestions = data[1] if isinstance(data, list) and len(data) > 1 else []

                    # Each suggestion is its own signal for clustering
                    for suggestion in suggestions[:15]:
                        if not suggestion or len(suggestion) < 5:
                            continue
                        signals.append({
                            "source_type": self.source_type,
                            "query": suggestion,
                            "region": region,
                            "raw_data": {
                                "seed_query": query,
                                "suggestion": suggestion,
                            },
                            "status": "raw",
                            "ingested_at": datetime.now(UTC).isoformat(),
                        })

                    self._consecutive_errors = 0
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
