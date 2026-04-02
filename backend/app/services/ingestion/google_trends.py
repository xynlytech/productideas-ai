import asyncio
import logging
from datetime import UTC, datetime
from typing import Any

import httpx

from app.services.ingestion import BaseSourceConnector, register_connector

logger = logging.getLogger(__name__)

GOOGLE_TRENDS_DAILY_URL = "https://trends.google.com/trends/api/dailytrends"
GOOGLE_TRENDS_INTEREST_URL = "https://trends.google.com/trends/api/widgetdata/multiline"


class GoogleTrendsConnector(BaseSourceConnector):
    source_type = "google_trends"

    def __init__(self):
        self._last_fetch: datetime | None = None
        self._consecutive_errors = 0

    async def fetch(self, queries: list[str], region: str = "US") -> list[dict[str, Any]]:
        signals = []
        async with httpx.AsyncClient(timeout=30.0) as client:
            for query in queries:
                try:
                    # Fetch daily trends related to the query
                    response = await client.get(
                        GOOGLE_TRENDS_DAILY_URL,
                        params={
                            "hl": "en-US",
                            "tz": "-300",
                            "geo": region,
                            "ns": "15",
                        },
                        headers={"Accept": "application/json"},
                    )
                    response.raise_for_status()

                    # Google Trends prepends ")]}'" to JSON responses
                    raw_text = response.text
                    if raw_text.startswith(")]}'"):
                        raw_text = raw_text[5:]

                    signals.append({
                        "source_type": self.source_type,
                        "query": query,
                        "region": region,
                        "raw_data": {"response_text": raw_text[:10000]},
                        "status": "raw",
                        "ingested_at": datetime.now(UTC).isoformat(),
                    })
                    self._consecutive_errors = 0

                    # Rate limiting: 1 request per 2 seconds
                    await asyncio.sleep(2)

                except httpx.HTTPStatusError as e:
                    self._consecutive_errors += 1
                    logger.warning(f"Google Trends HTTP error for '{query}': {e.response.status_code}")
                    if e.response.status_code == 429:
                        logger.info("Rate limited by Google Trends, backing off 60s")
                        await asyncio.sleep(60)
                except Exception as e:
                    self._consecutive_errors += 1
                    logger.error(f"Google Trends error for '{query}': {e}")

        self._last_fetch = datetime.now(UTC)
        return signals

    async def health_check(self) -> dict:
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get("https://trends.google.com/trends/", follow_redirects=True)
                reachable = resp.status_code < 500
        except Exception:
            reachable = False

        return {
            "healthy": reachable and self._consecutive_errors < 5,
            "reachable": reachable,
            "consecutive_errors": self._consecutive_errors,
            "last_fetch": self._last_fetch.isoformat() if self._last_fetch else None,
        }


# Auto-register on import
_connector = GoogleTrendsConnector()
register_connector(_connector)
