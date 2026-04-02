"""One-off script to run the full data pipeline and populate Supabase."""
import asyncio
import logging

logging.basicConfig(level=logging.INFO)

from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.services.pipeline import run_full_pipeline

settings = get_settings()
engine = create_engine(settings.database_url_sync)

SEED_QUERIES = [
    "best saas tools 2026",
    "how to automate",
    "product ideas for developers",
    "side project ideas",
    "profitable online business",
    "trending products to sell",
    "problems worth solving",
    "unmet customer needs",
    "growing market niches",
    "what people are searching for",
    "ai tools for small business",
    "remote work productivity",
    "health tech startup ideas",
    "sustainable products trending",
    "fintech app ideas",
]


def main():
    with Session(engine) as db_session:
        result = asyncio.run(
            run_full_pipeline(queries=SEED_QUERIES, region="US", db_session=db_session)
        )
        print(f"\n=== PIPELINE RESULT ===")
        for k, v in result.items():
            print(f"  {k}: {v}")


if __name__ == "__main__":
    main()
