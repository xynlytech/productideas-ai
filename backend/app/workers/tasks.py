import json
import logging
from datetime import UTC, datetime

from app.core.config import get_settings
from app.workers import celery_app

logger = logging.getLogger(__name__)
settings = get_settings()


@celery_app.task(name="app.workers.tasks.run_ingestion_pipeline")
def run_ingestion_pipeline():
    """Run the full ingestion → normalization → clustering → scoring pipeline."""
    import asyncio

    from sqlalchemy import create_engine
    from sqlalchemy.orm import Session

    from app.services.pipeline import run_full_pipeline

    engine = create_engine(settings.database_url_sync)

    # Default seed queries for discovery
    seed_queries = [
        "best saas tools 2026",
        "how to automate",
        "product ideas",
        "side project ideas",
        "profitable business ideas",
        "trending products",
        "problems worth solving",
        "unmet needs",
        "growing markets",
        "what people are searching for",
    ]

    with Session(engine) as db_session:
        result = asyncio.get_event_loop().run_until_complete(
            run_full_pipeline(queries=seed_queries, region="US", db_session=db_session)
        )

    logger.info(f"Ingestion pipeline result: {result}")
    return result


@celery_app.task(name="app.workers.tasks.rebuild_all_scores")
def rebuild_all_scores():
    """Recalculate scores for all existing ideas."""
    from sqlalchemy import create_engine
    from sqlalchemy.orm import Session

    from app.models.opportunity_idea import OpportunityIdea
    from app.services.scoring import compute_opportunity_score

    engine = create_engine(settings.database_url_sync)

    with Session(engine) as db_session:
        ideas = db_session.query(OpportunityIdea).all()
        updated = 0
        for idea in ideas:
            scores = compute_opportunity_score(
                demand_growth=idea.demand_growth_score,
                query_volume=idea.query_volume,
                pain_intensity=idea.pain_intensity_score,
                momentum=idea.momentum_score,
                competition_saturation=idea.competition_score,
                confidence=idea.confidence_score,
            )
            idea.opportunity_score = scores["opportunity_score"]
            idea.score_label = scores["score_label"]
            idea.ranking_reason = scores["ranking_reason"]
            idea.confidence_caveats = scores["confidence_caveats"]
            updated += 1
        db_session.commit()

    logger.info(f"Rebuilt scores for {updated} ideas")
    return {"updated": updated}


@celery_app.task(name="app.workers.tasks.generate_export")
def generate_export(export_id: int):
    """Generate a CSV/PDF export file."""
    import csv
    import io

    from sqlalchemy import create_engine
    from sqlalchemy.orm import Session

    from app.models.export import Export
    from app.models.opportunity_idea import OpportunityIdea

    engine = create_engine(settings.database_url_sync)

    with Session(engine) as db_session:
        export = db_session.query(Export).get(export_id)
        if not export:
            logger.error(f"Export {export_id} not found")
            return

        export.status = "processing"
        db_session.commit()

        try:
            # Fetch ideas based on filters
            query = db_session.query(OpportunityIdea)
            if export.filters_used:
                filters = json.loads(export.filters_used)
                if filters.get("category"):
                    query = query.filter(OpportunityIdea.category == filters["category"])
                if filters.get("min_score"):
                    query = query.filter(
                        OpportunityIdea.opportunity_score >= filters["min_score"]
                    )
            ideas = query.order_by(OpportunityIdea.opportunity_score.desc()).limit(500).all()

            if export.format == "csv":
                output = io.StringIO()
                writer = csv.writer(output)
                writer.writerow([
                    "Title", "Score", "Label", "Category", "Region",
                    "Demand Growth", "Competition", "Pain Intensity",
                    "Confidence", "Momentum", "Problem Statement",
                ])
                for idea in ideas:
                    writer.writerow([
                        idea.title, idea.opportunity_score, idea.score_label,
                        idea.category, idea.region,
                        idea.demand_growth_score, idea.competition_score,
                        idea.pain_intensity_score, idea.confidence_score,
                        idea.momentum_score, idea.problem_statement,
                    ])
                # In production, upload to S3 and store URL
                export.file_url = f"/exports/{export_id}.csv"
            else:
                # PDF generation placeholder
                export.file_url = f"/exports/{export_id}.pdf"

            export.status = "completed"
            export.completed_at = datetime.now(UTC)
        except Exception as e:
            logger.error(f"Export {export_id} failed: {e}")
            export.status = "failed"

        db_session.commit()

    logger.info(f"Export {export_id} completed")
    return {"export_id": export_id, "status": export.status}


@celery_app.task(name="app.workers.tasks.evaluate_alerts")
def evaluate_alerts():
    """Check alerts against recent ideas and flag triggered ones."""
    from sqlalchemy import and_, create_engine
    from sqlalchemy.orm import Session

    from app.models.alert import Alert
    from app.models.opportunity_idea import OpportunityIdea

    engine = create_engine(settings.database_url_sync)

    with Session(engine) as db_session:
        active_alerts = db_session.query(Alert).filter(Alert.is_active.is_(True)).all()
        triggered = 0

        for alert in active_alerts:
            query = db_session.query(OpportunityIdea)

            conditions = []
            if alert.keyword:
                conditions.append(
                    OpportunityIdea.title.ilike(f"%{alert.keyword}%")
                )
            if alert.category:
                conditions.append(OpportunityIdea.category == alert.category)
            if alert.region:
                conditions.append(OpportunityIdea.region == alert.region)
            if alert.min_score is not None:
                conditions.append(
                    OpportunityIdea.opportunity_score >= alert.min_score
                )

            # Only check ideas created since last trigger
            if alert.last_triggered_at:
                conditions.append(
                    OpportunityIdea.created_at > alert.last_triggered_at
                )

            if conditions:
                matches = query.filter(and_(*conditions)).count()
                if matches > 0:
                    alert.last_triggered_at = datetime.now(UTC)
                    triggered += 1

        db_session.commit()

    logger.info(f"Evaluated {len(active_alerts)} alerts, {triggered} triggered")
    return {"evaluated": len(active_alerts), "triggered": triggered}
