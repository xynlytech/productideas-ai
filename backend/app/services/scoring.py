import logging
import math

logger = logging.getLogger(__name__)

# Score thresholds
SCORE_LABELS = {
    (80, 100): "Very Strong",
    (60, 79): "Promising",
    (40, 59): "Weak Signal",
    (0, 39): "Low Priority",
}


def compute_opportunity_score(
    demand_growth: float,
    query_volume: int,
    pain_intensity: float,
    momentum: float,
    competition_saturation: float,
    confidence: float,
) -> dict:
    """
    Compute the opportunity score using the formula:
    Score = ((Demand Growth × Query Volume × Pain Intensity × Momentum) / Competition Saturation) × Confidence

    All sub-scores are normalized to 0-100 before the final composite.

    Returns a dict with all score components.
    """
    # Clamp inputs to valid ranges
    demand_growth = max(0.0, min(100.0, demand_growth))
    pain_intensity = max(0.0, min(100.0, pain_intensity))
    momentum = max(0.0, min(100.0, momentum))
    competition_saturation = max(1.0, min(100.0, competition_saturation))  # min 1 to avoid division by zero
    confidence = max(0.0, min(100.0, confidence))
    query_volume = max(0, query_volume)

    # Normalize query volume to 0-100 (log scale, assuming max ~1M)
    volume_normalized = min(100.0, (math.log10(query_volume + 1) / 6.0) * 100)

    # Composite numerator (geometric mean approach for balanced scoring)
    numerator = (
        (demand_growth / 100)
        * (volume_normalized / 100)
        * (pain_intensity / 100)
        * (momentum / 100)
    )

    denominator = competition_saturation / 100
    confidence_multiplier = confidence / 100

    # Raw score (0 to 1 range) → normalize to 0-100
    raw = (numerator / denominator) * confidence_multiplier
    # Apply sqrt to spread out the distribution
    normalized = min(100.0, math.sqrt(raw) * 100)
    final_score = round(normalized, 1)

    # Determine label
    score_label = "Low Priority"
    for (low, high), label in SCORE_LABELS.items():
        if low <= final_score <= high:
            score_label = label
            break

    # Generate ranking reason
    top_factors = sorted(
        [
            ("demand growth", demand_growth),
            ("query volume", volume_normalized),
            ("pain intensity", pain_intensity),
            ("momentum", momentum),
        ],
        key=lambda x: x[1],
        reverse=True,
    )
    ranking_reason = f"Driven primarily by {top_factors[0][0]} ({top_factors[0][1]:.0f}/100) and {top_factors[1][0]} ({top_factors[1][1]:.0f}/100)."

    # Confidence caveats
    caveats = []
    if confidence < 40:
        caveats.append("Low confidence — limited data signals available.")
    if query_volume < 100:
        caveats.append("Low search volume — early signal, may not sustain.")
    if competition_saturation > 80:
        caveats.append("High competition — differentiation critical.")

    return {
        "opportunity_score": final_score,
        "demand_growth_score": round(demand_growth, 1),
        "competition_score": round(competition_saturation, 1),
        "pain_intensity_score": round(pain_intensity, 1),
        "confidence_score": round(confidence, 1),
        "momentum_score": round(momentum, 1),
        "query_volume": query_volume,
        "score_label": score_label,
        "ranking_reason": ranking_reason,
        "confidence_caveats": "; ".join(caveats) if caveats else None,
    }


def score_cluster(cluster: dict) -> dict:
    """
    Score an entire cluster by analyzing its signals and keywords.
    Returns score components to be stored on an OpportunityIdea.
    """
    signals = cluster.get("signals", [])
    keywords = cluster.get("keywords", [])

    # Estimate sub-scores from available signal data
    num_signals = len(signals)
    num_keywords = len(keywords)

    # Source diversity bonus: more sources = higher confidence signal
    sources = {s.get("source_type", "") for s in signals}
    source_diversity = len(sources)

    # Aggregate real engagement data from Reddit/HN signals
    total_upvotes = 0
    total_comments = 0
    for s in signals:
        raw = s.get("raw_data", {})
        total_upvotes += raw.get("score", 0)  # Reddit upvotes or HN points
        total_comments += raw.get("num_comments", 0)

    # Demand growth: signals across multiple sources with real engagement
    demand_growth = min(100, num_signals * 8 + source_diversity * 15 + 10)

    # Query volume: real upvotes/points indicate true demand magnitude
    # Log-scale so a HN post with 500 points doesn't dominate
    if total_upvotes > 0:
        import math
        query_volume = int(min(1_000_000, math.exp(min(14, math.log(total_upvotes + 1) * 2.5)) * 100))
    else:
        query_volume = max(100, num_signals * 200)

    # Pain intensity: comment count signals how much people care (more discussion = more pain)
    comment_signal = min(50, total_comments / 10)
    avg_keyword_length = sum(len(k["keyword"]) for k in keywords) / max(1, num_keywords)
    pain_intensity = min(100, comment_signal + avg_keyword_length * 2 + num_signals * 5)

    # Momentum: signals from multiple recent sources boost momentum
    momentum = min(100, num_signals * 7 + source_diversity * 20 + 20)

    # Competition: estimated from keyword specificity; specific = less saturated
    competition = max(10, 100 - pain_intensity + 15)

    # Confidence: multi-source signals with engagement are most reliable
    confidence = min(100, num_signals * 12 + num_keywords * 3 + source_diversity * 10)

    return compute_opportunity_score(
        demand_growth=demand_growth,
        query_volume=query_volume,
        pain_intensity=pain_intensity,
        momentum=momentum,
        competition_saturation=competition,
        confidence=confidence,
    )
