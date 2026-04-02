from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.topic_cluster import TopicCluster
from app.schemas.ideas import ClusterListResponse, ClusterResponse

router = APIRouter(prefix="/clusters", tags=["clusters"])


@router.get("", response_model=list[ClusterListResponse])
async def list_clusters(
    db: AsyncSession = Depends(get_db),
    _user=Depends(get_current_user),
    category: str | None = None,
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
):
    query = select(TopicCluster)
    if category:
        query = query.where(TopicCluster.category == category)
    query = query.order_by(TopicCluster.idea_count.desc())
    query = query.offset((page - 1) * limit).limit(limit)

    result = await db.execute(query)
    return [ClusterListResponse.model_validate(c) for c in result.scalars().all()]


@router.get("/{cluster_id}", response_model=ClusterResponse)
async def get_cluster(
    cluster_id: int,
    db: AsyncSession = Depends(get_db),
    _user=Depends(get_current_user),
):
    result = await db.execute(
        select(TopicCluster).where(TopicCluster.id == cluster_id)
    )
    cluster = result.scalar_one_or_none()
    if not cluster:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cluster not found")
    return ClusterResponse.model_validate(cluster)
