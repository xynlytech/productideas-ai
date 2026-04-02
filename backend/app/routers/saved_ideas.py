from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.saved_idea import SavedIdea
from app.models.user import User
from app.schemas.saved_ideas import SavedIdeaCreate, SavedIdeaResponse, SavedIdeaUpdate

router = APIRouter(prefix="/saved-ideas", tags=["saved-ideas"])


@router.get("", response_model=list[SavedIdeaResponse])
async def list_saved_ideas(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(SavedIdea)
        .where(SavedIdea.user_id == current_user.id)
        .order_by(SavedIdea.created_at.desc())
    )
    return [SavedIdeaResponse.model_validate(s) for s in result.scalars().all()]


@router.post("", response_model=SavedIdeaResponse, status_code=status.HTTP_201_CREATED)
async def save_idea(
    data: SavedIdeaCreate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    # Check for duplicate
    existing = await db.execute(
        select(SavedIdea).where(
            SavedIdea.user_id == current_user.id,
            SavedIdea.idea_id == data.idea_id,
        )
    )
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Idea already saved"
        )

    saved = SavedIdea(user_id=current_user.id, idea_id=data.idea_id, note=data.note)
    db.add(saved)
    await db.flush()
    await db.refresh(saved, ["idea"])
    return SavedIdeaResponse.model_validate(saved)


@router.patch("/{saved_id}", response_model=SavedIdeaResponse)
async def update_saved_idea(
    saved_id: int,
    data: SavedIdeaUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(SavedIdea).where(
            SavedIdea.id == saved_id, SavedIdea.user_id == current_user.id
        )
    )
    saved = result.scalar_one_or_none()
    if not saved:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Saved idea not found")

    if data.note is not None:
        saved.note = data.note
    await db.flush()
    await db.refresh(saved, ["idea"])
    return SavedIdeaResponse.model_validate(saved)


@router.delete("/{saved_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_saved_idea(
    saved_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = await db.execute(
        select(SavedIdea).where(
            SavedIdea.id == saved_id, SavedIdea.user_id == current_user.id
        )
    )
    saved = result.scalar_one_or_none()
    if not saved:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Saved idea not found")
    await db.delete(saved)
