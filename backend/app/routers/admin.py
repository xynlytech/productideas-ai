from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import require_admin
from app.models.audit_log import AuditLog

router = APIRouter(prefix="/admin", tags=["admin"])


async def create_audit_log(
    db: AsyncSession,
    action: str,
    user_id: int | None,
    resource_type: str | None = None,
    resource_id: int | None = None,
    details: str | None = None,
    ip_address: str | None = None,
):
    """Helper to create audit log entries."""
    log = AuditLog(
        user_id=user_id,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        details=details,
        ip_address=ip_address,
    )
    db.add(log)
    await db.flush()


@router.post("/ingestion/run")
async def trigger_ingestion(
    request: Request,
    _admin=Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    from app.workers.tasks import run_ingestion_pipeline

    task = run_ingestion_pipeline.delay()

    # Log the action
    await create_audit_log(
        db=db,
        action="ingestion_triggered",
        user_id=_admin.id if hasattr(_admin, "id") else None,
        resource_type="pipeline",
        details=f"Ingestion pipeline started with task_id: {task.id}",
        ip_address=request.client.host if request.client else None,
    )

    return {"message": "Ingestion pipeline triggered", "task_id": str(task.id)}


@router.post("/scoring/rebuild")
async def rebuild_scores(
    request: Request,
    _admin=Depends(require_admin),
    db: AsyncSession = Depends(get_db),
):
    from app.workers.tasks import rebuild_all_scores

    task = rebuild_all_scores.delay()

    # Log the action
    await create_audit_log(
        db=db,
        action="scores_rebuilt",
        user_id=_admin.id if hasattr(_admin, "id") else None,
        resource_type="scoring",
        details=f"Score rebuild initiated with task_id: {task.id}",
        ip_address=request.client.host if request.client else None,
    )

    return {"message": "Score rebuild triggered", "task_id": str(task.id)}


@router.get("/sources")
async def get_source_health(_admin=Depends(require_admin)):
    from app.services.ingestion.base import get_all_source_status
    return await get_all_source_status()
