"""
Reddit connector — uses the public Reddit JSON API (no authentication required).
Targets entrepreneurship/startup/SaaS subreddits to surface real pain points
and product ideas from the community.
"""
import asyncio
import logging
from datetime import UTC, datetime
from typing import Any

import httpx

from app.services.ingestion import BaseSourceConnector, register_connector

logger = logging.getLogger(__name__)

# Subreddits rich in product/startup signals — public, no auth needed
SUBREDDITS = [
    ("entrepreneur", "top", "week"),
    ("SaaS", "top", "week"),
    ("startups", "top", "week"),
    ("SideProject", "top", "month"),
    ("smallbusiness", "top", "week"),
    ("Entrepreneur", "new", None),
    ("nocode", "top", "week"),
    ("artificial", "top", "week"),
    ("ProductHunters", "top", "month"),
]

# Minimum score to include a post as a signal
MIN_SCORE = 5
# Max posts to pull per subreddit
POSTS_PER_SUB = 25

REDDIT_USER_AGENT = "productideas-bot/1.0 (data pipeline; contact via github)"


class RedditConnector(BaseSourceConnector):
    source_type = "reddit"

    def __init__(self):
        self._last_fetch: datetime | None = None
        self._consecutive_errors = 0

    async def fetch(self, queries: list[str], region: str = "US") -> list[dict[str, Any]]:
        """
        Pull top/new posts from curated subreddits.
        `queries` is ignored — we pull real community posts directly.
        Each post title becomes a signal; upvotes and comments become metadata.
        """
        signals = []

        async with httpx.AsyncClient(
            timeout=20.0,
            headers={
                "User-Agent": REDDIT_USER_AGENT,
                "Accept": "application/json",
            },
            follow_redirects=True,
        ) as client:
            for subreddit, sort, timeframe in SUBREDDITS:
                try:
                    url = f"https://www.reddit.com/r/{subreddit}/{sort}.json"
                    params: dict[str, Any] = {"limit": POSTS_PER_SUB}
                    if timeframe:
                        params["t"] = timeframe

                    response = await client.get(url, params=params)
                    response.raise_for_status()

                    data = response.json()
                    posts = data.get("data", {}).get("children", [])

                    for post in posts:
                        p = post.get("data", {})

                        score = p.get("score", 0)
                        if score < MIN_SCORE:
                            continue

                        title = p.get("title", "").strip()
                        if not title:
                            continue

                        # Skip image/video-only posts with no text content
                        selftext = p.get("selftext", "").strip()
                        post_hint = p.get("post_hint", "")
                        if post_hint in ("image", "video", "link") and not selftext:
                            continue

                        signals.append({
                            "source_type": self.source_type,
                            "query": title,
                            "region": region,
                            "raw_data": {
                                "subreddit": subreddit,
                                "score": score,
                                "num_comments": p.get("num_comments", 0),
                                "upvote_ratio": p.get("upvote_ratio", 0.5),
                                "selftext": selftext[:500] if selftext else "",
                                "url": f"https://reddit.com{p.get('permalink', '')}",
                                "flair": p.get("link_flair_text", ""),
                                "sort": sort,
                                "timeframe": timeframe,
                            },
                            "status": "raw",
                            "ingested_at": datetime.now(UTC).isoformat(),
                        })

                    self._consecutive_errors = 0
                    logger.info(
                        f"Reddit r/{subreddit}: extracted {len([s for s in signals if s['raw_data'].get('subreddit') == subreddit])} signals"
                    )

                    # Reddit recommends 1 req/2s for unauthenticated
                    await asyncio.sleep(2)

                except httpx.HTTPStatusError as e:
                    self._consecutive_errors += 1
                    if e.response.status_code == 429:
                        logger.warning("Reddit rate limited, backing off 30s")
                        await asyncio.sleep(30)
                    elif e.response.status_code == 403:
                        logger.warning(f"Reddit r/{subreddit} is private or banned, skipping")
                    else:
                        logger.warning(f"Reddit HTTP {e.response.status_code} for r/{subreddit}")
                except Exception as e:
                    self._consecutive_errors += 1
                    logger.error(f"Reddit error for r/{subreddit}: {e}")

        self._last_fetch = datetime.now(UTC)
        logger.info(f"Reddit: total {len(signals)} signals ingested")
        return signals

    async def health_check(self) -> dict:
        try:
            async with httpx.AsyncClient(
                timeout=10.0,
                headers={"User-Agent": REDDIT_USER_AGENT},
                follow_redirects=True,
            ) as client:
                resp = await client.get("https://www.reddit.com/r/entrepreneur/top.json?limit=1&t=week")
                reachable = resp.status_code < 500
        except Exception:
            reachable = False

        return {
            "healthy": reachable and self._consecutive_errors < 5,
            "reachable": reachable,
            "consecutive_errors": self._consecutive_errors,
            "last_fetch": self._last_fetch.isoformat() if self._last_fetch else None,
        }


_connector = RedditConnector()
register_connector(_connector)
