from celery import Celery

from app.core.config import get_settings

settings = get_settings()

celery_app = Celery(
    "productideas",
    broker=settings.redis_url,
    backend=settings.redis_url,
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    beat_schedule={
        "daily-ingestion": {
            "task": "app.workers.tasks.run_ingestion_pipeline",
            "schedule": 86400.0,  # 24 hours
        },
    },
)

# Import tasks so they are registered
celery_app.autodiscover_tasks(["app.workers"])
