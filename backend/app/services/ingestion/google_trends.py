import asyncio
import json
import logging
from datetime import UTC, datetime
from typing import Any

import httpx

from app.services.ingestion import BaseSourceConnector, register_connector

logger = logging.getLogger(__name__)

GOOGLE_TRENDS_DAILY_URL = "https://trends.google.com/trends/api/dailytrends"

# Real-time trending search categories mapped to region
TRENDING_REGIONS = ["US", "GB", "AU", "CA", "IN"]


def _strip_prefix(text: str) -> str:
    """Google Trends API responses start with )]}' followed by a newline."""
    if text.startswith(")]}'"):
        return text[5:].lstrip("\n")
    return text


class GoogleTrendsConnector(BaseSourceConnector):
    source_type = "google_trends"

    def __init__(self):
        self._last_fetch: datetime | None = None
        self._consecutive_errors = 0

    async def fetch(self, queries: list[str], region: str = "US") -> list[dict[str, Any]]:
        """
        Fetch real daily trending searches from Google Trends.
        Each trending topic becomes its own signal for downstream processing.
        `queries` is used as topic hints but we always pull the live daily trends.
        """
        signals = []

        async with httpx.AsyncClient(
            timeout=30.0,
            headers={
                "User-Agent": (
                    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                    "AppleWebKit/537.36 (KHTML, like Gecko) "
                    "Chrome/122.0.0.0 Safari/537.36"
                ),
                "Accept-Language": "en-US,en;q=0.9",
            },
            follow_redirects=True,
        ) as client:
            try:
                response = await client.get(
                    GOOGLE_TRENDS_DAILY_URL,
                    params={
                        "hl": "en-US",
                        "tz": "-300",
                        "geo": region,
                        "ns": "15",
                    },
                )
                response.raise_for_status()

                raw_json = _strip_prefix(response.text)
                data = json.loads(raw_json)

                trending_days = (
                    data.get("default", {})
                    .get("trendingSearchesDays", [])
                )

                for day in trending_days[:2]:  # last 2 days
                    for trend in day.get("trendingSearches", []):
                        title_obj = trend.get("title", {})
                        topic_title = title_obj.get("query", "").strip()
                        if not topic_title:
                            continue

                        traffic = trend.get("formattedTraffic", "")
                        related_queries = [
                            rq.get("query", "")
                            for rq in trend.get("relatedQueries", [])
                            if rq.get("query")
                        ]
                        articles = [
                            {
                                "title": a.get("title", ""),
                                "source": a.get("source", {}).get("name", ""),
                                "url": a.get("url", ""),
                            }
                            for a in trend.get("articles", [])[:3]
                        ]

                        signals.append({
                            "source_type": self.source_type,
                            "query": topic_title,
                            "region": region,
                            "raw_data": {
                                "traffic": traffic,
                                "related_queries": related_queries,
                                "articles": articles,
                                "date": day.get("date", ""),
                            },
                            "status": "raw",
                            "ingested_at": datetime.now(UTC).isoformat(),
                        })

                self._consecutive_errors = 0
                logger.info(
                    f"Google Trends: extracted {len(signals)} trending topics for region={region}"
                )

                # Polite rate limit
                await asyncio.sleep(2)

            except httpx.HTTPStatusError as e:
                self._consecutive_errors += 1
                logger.warning(
                    f"Google Trends HTTP error {e.response.status_code} for region={region}"
                )
                if e.response.status_code == 429:
                    logger.info("Rate limited by Google Trends, backing off 60s")
                    await asyncio.sleep(60)
            except json.JSONDecodeError as e:
                self._consecutive_errors += 1
                logger.error(f"Google Trends JSON parse error: {e}")
            except Exception as e:
                self._consecutive_errors += 1
                logger.error(f"Google Trends error: {e}")

        self._last_fetch = datetime.now(UTC)
        return signals

    async def health_check(self) -> dict:
        try:
            async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
                resp = await client.get("https://trends.google.com/trends/")
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
