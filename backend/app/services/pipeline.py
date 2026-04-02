import json
import logging
from datetime import UTC, datetime

from sqlalchemy.orm import Session

from app.models.cluster_keyword import ClusterKeyword
from app.models.opportunity_idea import OpportunityIdea
from app.models.source_signal import SourceSignal
from app.models.topic_cluster import TopicCluster
from app.services.clustering import cluster_signals
from app.services.normalization import normalize_batch
from app.services.scoring import score_cluster

logger = logging.getLogger(__name__)


async def run_full_pipeline(
    queries: list[str],
    region: str = "US",
    db_session: Session | None = None,
) -> dict:
    """
    Execute the full data pipeline:
    1. Ingest from all sources
    2. Normalize signals
    3. Cluster into topics
    4. Score opportunities
    5. Persist to database

    Returns pipeline summary.
    """
    # 1. Ingestion
    logger.info(f"Starting ingestion for {len(queries)} queries in {region}")

    # Import connectors (triggers registration)
    from app.services.ingestion import (  # noqa: F401
        get_connector,
        google_autocomplete,
        google_trends,
    )

    all_signals = []
    for source_type in ["google_trends", "google_autocomplete"]:
        try:
            connector = get_connector(source_type)
            signals = await connector.fetch(queries, region)
            all_signals.extend(signals)
            logger.info(f"Ingested {len(signals)} signals from {source_type}")
        except Exception as e:
            logger.error(f"Ingestion failed for {source_type}: {e}")

    if not all_signals:
        logger.warning("No signals ingested, pipeline stopping.")
        return {"status": "empty", "signals_ingested": 0}

    # 2. Normalization
    normalized = normalize_batch(all_signals)
    logger.info(f"Normalized to {len(normalized)} signals")

    # 3. Clustering
    clusters = cluster_signals(normalized)
    logger.info(f"Produced {len(clusters)} clusters")

    # 4. Scoring & 5. Persistence
    ideas_created = 0
    if db_session:
        for cluster_data in clusters:
            scores = score_cluster(cluster_data)

            # Create or update TopicCluster
            tc = TopicCluster(
                label=cluster_data["label"],
                description=f"Cluster around: {cluster_data['label']}",
                category=cluster_data.get("category"),
                idea_count=len(cluster_data["signals"]),
            )
            db_session.add(tc)
            db_session.flush()

            # Add keywords
            for kw in cluster_data["keywords"]:
                ckw = ClusterKeyword(
                    cluster_id=tc.id,
                    keyword=kw["keyword"],
                    weight=kw["weight"],
                )
                db_session.add(ckw)

            # Create OpportunityIdea
            idea = OpportunityIdea(
                cluster_id=tc.id,
                title=_generate_title(cluster_data),
                problem_statement=_generate_problem(cluster_data),
                why_it_matters=_generate_rationale(cluster_data),
                suggested_product=_generate_product_suggestion(cluster_data),
                category=cluster_data.get("category"),
                region=region,
                trend_type="rising",
                trend_data=json.dumps(_extract_trend_points(cluster_data)),
                signals_summary=json.dumps([s["query"] for s in cluster_data["signals"][:10]]),
                **scores,
            )
            db_session.add(idea)
            ideas_created += 1

            # Store raw signals
            for s in cluster_data["signals"]:
                signal = SourceSignal(
                    source_type=s["source_type"],
                    query=s["query"],
                    region=s.get("region"),
                    raw_data=s.get("raw_data"),
                    status="processed",
                    processed_at=datetime.now(UTC),
                )
                db_session.add(signal)

        db_session.commit()

    logger.info(f"Pipeline complete: {ideas_created} ideas created from {len(clusters)} clusters")
    return {
        "status": "success",
        "signals_ingested": len(all_signals),
        "signals_normalized": len(normalized),
        "clusters_formed": len(clusters),
        "ideas_created": ideas_created,
    }


def _generate_title(cluster: dict) -> str:
    label = cluster["label"]
    return label.title() if len(label) < 80 else label[:77].title() + "..."


def _generate_problem(cluster: dict) -> str:
    keywords = [k["keyword"] for k in cluster["keywords"][:5]]
    return (
        f"People are actively searching for solutions related to "
        f"'{cluster['label']}'. Related searches include: {', '.join(keywords)}. "
        f"This signals unmet demand in this space."
    )


def _generate_rationale(cluster: dict) -> str:
    n_signals = len(cluster["signals"])
    n_keywords = len(cluster["keywords"])
    return (
        f"This opportunity is backed by {n_signals} search signals across "
        f"{n_keywords} related keywords, indicating sustained interest. "
        f"The search patterns suggest real user problems waiting for solutions."
    )


def _generate_product_suggestion(cluster: dict) -> str:
    category = cluster.get("category") or "digital product"
    return (
        f"Consider building a {category.lower()} solution that addresses "
        f"the core need expressed in '{cluster['label']}'. "
        f"Focus on the specific pain points revealed by search intent."
    )


def _extract_trend_points(cluster: dict) -> list[dict]:
    # Placeholder trend data — in production, extracted from Google Trends time series
    return [
        {"date": "2026-01", "value": 45},
        {"date": "2026-02", "value": 58},
        {"date": "2026-03", "value": 72},
    ]
