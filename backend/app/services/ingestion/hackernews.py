"""
HackerNews connector — uses the official HN Firebase REST API (free, no auth).
Targets "Ask HN" posts and top stories to surface real problems and product gaps.
"""
import asyncio
import logging
from datetime import UTC, datetime
from typing import Any

import httpx

from app.services.ingestion import BaseSourceConnector, register_connector

logger = logging.getLogger(__name__)

HN_BASE = "https://hacker-news.firebaseio.com/v2"
HN_ALGOLIA = "https://hn.algolia.com/api/v1"

# How many top/ask stories to pull
TOP_STORIES_LIMIT = 60
ASK_STORIES_LIMIT = 40

# Minimum score to include
MIN_SCORE = 10


class HackerNewsConnector(BaseSourceConnector):
    source_type = "hackernews"

    def __init__(self):
        self._last_fetch: datetime | None = None
        self._consecutive_errors = 0

    async def _fetch_item(self, client: httpx.AsyncClient, item_id: int) -> dict | None:
        try:
            resp = await client.get(f"{HN_BASE}/item/{item_id}.json")
            resp.raise_for_status()
            return resp.json()
        except Exception:
            return None

    async def _fetch_ask_hn_via_algolia(self, client: httpx.AsyncClient) -> list[dict]:
        """
        Use Algolia HN Search API to pull recent Ask HN posts —
        these are the richest signals for unmet needs.
        """
        try:
            resp = await client.get(
                f"{HN_ALGOLIA}/search",
                params={
                    "query": "Ask HN",
                    "tags": "ask_hn",
                    "hitsPerPage": ASK_STORIES_LIMIT,
                    "numericFilters": f"points>{MIN_SCORE}",
                },
            )
            resp.raise_for_status()
            hits = resp.json().get("hits", [])
            return hits
        except Exception as e:
            logger.warning(f"HN Algolia fetch failed: {e}")
            return []

    async def fetch(self, queries: list[str], region: str = "US") -> list[dict[str, Any]]:
        """
        Pull top HN stories + Ask HN posts. Each story title becomes a signal.
        Ask HN posts are especially valuable as they represent direct "I need X" requests.
        """
        signals = []

        async with httpx.AsyncClient(
            timeout=20.0,
            headers={"User-Agent": "productideas-bot/1.0"},
            follow_redirects=True,
        ) as client:
            # ── 1. Top stories ─────────────────────────────────────────────
            try:
                resp = await client.get(f"{HN_BASE}/topstories.json")
                resp.raise_for_status()
                top_ids = resp.json()[:TOP_STORIES_LIMIT]
            except Exception as e:
                logger.error(f"HN top stories list failed: {e}")
                top_ids = []

            # Fetch items in small batches to respect the API
            for i in range(0, len(top_ids), 10):
                batch = top_ids[i : i + 10]
                items = await asyncio.gather(
                    *[self._fetch_item(client, item_id) for item_id in batch],
                    return_exceptions=False,
                )
                for item in items:
                    if not item or item.get("type") != "story":
                        continue
                    if item.get("score", 0) < MIN_SCORE:
                        continue
                    title = (item.get("title") or "").strip()
                    if not title:
                        continue

                    signals.append({
                        "source_type": self.source_type,
                        "query": title,
                        "region": region,
                        "raw_data": {
                            "hn_id": item.get("id"),
                            "score": item.get("score", 0),
                            "num_comments": item.get("descendants", 0),
                            "url": item.get("url", f"https://news.ycombinator.com/item?id={item.get('id')}"),
                            "type": "top_story",
                            "by": item.get("by", ""),
                        },
                        "status": "raw",
                        "ingested_at": datetime.now(UTC).isoformat(),
                    })

                await asyncio.sleep(0.5)  # polite

            # ── 2. Ask HN posts via Algolia ─────────────────────────────────
            ask_hits = await self._fetch_ask_hn_via_algolia(client)
            for hit in ask_hits:
                title = (hit.get("title") or "").strip()
                if not title:
                    continue

                # Strip "Ask HN: " prefix for cleaner signal text
                clean_title = title.replace("Ask HN: ", "").replace("Ask HN:", "").strip()

                signals.append({
                    "source_type": self.source_type,
                    "query": clean_title,
                    "region": region,
                    "raw_data": {
                        "hn_id": hit.get("objectID"),
                        "score": hit.get("points", 0),
                        "num_comments": hit.get("num_comments", 0),
                        "url": f"https://news.ycombinator.com/item?id={hit.get('objectID')}",
                        "type": "ask_hn",
                        "original_title": title,
                        "story_text": (hit.get("story_text") or "")[:300],
                    },
                    "status": "raw",
                    "ingested_at": datetime.now(UTC).isoformat(),
                })

            self._consecutive_errors = 0
            logger.info(
                f"HackerNews: {len([s for s in signals if s['raw_data']['type'] == 'top_story'])} top stories, "
                f"{len([s for s in signals if s['raw_data']['type'] == 'ask_hn'])} Ask HN posts"
            )

        self._last_fetch = datetime.now(UTC)
        return signals

    async def health_check(self) -> dict:
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.get(f"{HN_BASE}/topstories.json")
                reachable = resp.status_code < 500
        except Exception:
            reachable = False

        return {
            "healthy": reachable and self._consecutive_errors < 5,
            "reachable": reachable,
            "consecutive_errors": self._consecutive_errors,
            "last_fetch": self._last_fetch.isoformat() if self._last_fetch else None,
        }


_connector = HackerNewsConnector()
register_connector(_connector)
