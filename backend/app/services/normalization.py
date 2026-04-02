import logging
import re
from datetime import UTC, datetime

logger = logging.getLogger(__name__)

# Common spam / junk patterns
JUNK_PATTERNS = [
    re.compile(r"^(https?://|www\.)", re.IGNORECASE),
    re.compile(r"\b(porn|xxx|nude|sex|casino|gambling)\b", re.IGNORECASE),
    re.compile(r"^.{1,2}$"),  # Too short
    re.compile(r"^[^a-zA-Z]*$"),  # No letters at all
]


def normalize_text(text: str) -> str:
    """Lowercase, strip whitespace, collapse spaces."""
    text = text.lower().strip()
    text = re.sub(r"\s+", " ", text)
    return text


def is_junk(text: str) -> bool:
    """Check if text matches known junk patterns."""
    return any(p.search(text) for p in JUNK_PATTERNS)


def deduplicate_signals(signals: list[dict]) -> list[dict]:
    """Remove exact duplicate signals by normalized query text."""
    seen = set()
    unique = []
    for signal in signals:
        key = normalize_text(signal.get("query", ""))
        if key not in seen:
            seen.add(key)
            unique.append(signal)
    return unique


def normalize_signal(signal: dict) -> dict | None:
    """
    Clean and normalize a single signal dict.
    Returns None if signal should be discarded.
    """
    query = signal.get("query", "")
    normalized = normalize_text(query)

    if not normalized or is_junk(normalized):
        logger.debug(f"Discarding junk signal: '{query}'")
        return None

    signal["query"] = normalized
    signal["status"] = "normalized"
    signal["processed_at"] = datetime.now(UTC).isoformat()

    # Normalize region
    region = signal.get("region", "")
    if region:
        signal["region"] = region.upper().strip()

    return signal


def normalize_batch(signals: list[dict]) -> list[dict]:
    """Normalize and deduplicate a batch of signals."""
    normalized = []
    for s in signals:
        result = normalize_signal(s)
        if result:
            normalized.append(result)

    deduped = deduplicate_signals(normalized)
    logger.info(f"Normalized {len(signals)} → {len(deduped)} signals ({len(signals) - len(deduped)} removed)")
    return deduped
