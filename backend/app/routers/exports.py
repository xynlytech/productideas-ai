import json

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.export import Export
from app.models.user import User
from app.schemas.exports import ExportCreate, ExportResponse

router = APIRouter(prefix="/exports", tags=["exports"])


@router.post("", response_model=ExportResponse, status_code=status.HTTP_202_ACCEPTED)
async def create_export(
    data: ExportCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    if data.format not in ("csv", "pdf"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Format must be csv or pdf"
        )

    export = Export(
        user_id=current_user.id,
        format=data.format,
        status="pending",
        filters_used=json.dumps(data.filters) if data.filters else None,
    )
    db.add(export)
    await db.flush()

    # Queue async export job
    from app.workers.tasks import generate_export
    generate_export.delay(export.id)

    return ExportResponse.model_validate(export)


@router.get("/{export_id}", response_model=ExportResponse)
async def get_export(
    export_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(Export).where(Export.id == export_id, Export.user_id == current_user.id)
    )
    export = result.scalar_one_or_none()
    if not export:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Export not found")
    return ExportResponse.model_validate(export)
