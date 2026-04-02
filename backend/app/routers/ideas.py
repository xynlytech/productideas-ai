import math

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.cache import CACHE_TTL_SHORT, _make_cache_key, cache_get, cache_set
from app.core.database import get_db
from app.core.security import get_current_user
from app.models.opportunity_idea import OpportunityIdea
from app.schemas.ideas import IdeaDetail, IdeaListItem, PaginatedIdeas

router = APIRouter(prefix="/ideas", tags=["ideas"])

SORT_COLUMNS = {
    "score": OpportunityIdea.opportunity_score,
    "recency": OpportunityIdea.created_at,
    "growth": OpportunityIdea.demand_growth_score,
    "confidence": OpportunityIdea.confidence_score,
    "momentum": OpportunityIdea.momentum_score,
}


@router.get("", response_model=PaginatedIdeas)
async def list_ideas(
    db: AsyncSession = Depends(get_db),
    _user=Depends(get_current_user),
    search: str | None = Query(None, max_length=200),
    category: str | None = None,
    region: str | None = None,
    trend_type: str | None = None,
    min_score: float | None = Query(None, ge=0, le=100),
    max_score: float | None = Query(None, ge=0, le=100),
    confidence_min: float | None = Query(None, ge=0, le=100),
    competition_max: float | None = Query(None, ge=0, le=100),
    sort: str = Query("score", pattern="^(score|recency|growth|confidence|momentum)$"),
    order: str = Query("desc", pattern="^(asc|desc)$"),
    page: int = Query(1, ge=1),
    limit: int = Query(20, ge=1, le=100),
):
    # Check cache
    cache_params = {
        "search": search, "category": category, "region": region,
        "trend_type": trend_type, "min_score": min_score, "max_score": max_score,
        "confidence_min": confidence_min, "competition_max": competition_max,
        "sort": sort, "order": order, "page": page, "limit": limit,
    }
    cache_key = _make_cache_key("ideas_list", cache_params)
    cached = await cache_get(cache_key)
    if cached:
        return PaginatedIdeas(**cached)

    query = select(OpportunityIdea)
    count_query = select(func.count(OpportunityIdea.id))

    # Filters
    if search:
        search_filter = or_(
            OpportunityIdea.title.ilike(f"%{search}%"),
            OpportunityIdea.problem_statement.ilike(f"%{search}%"),
        )
        query = query.where(search_filter)
        count_query = count_query.where(search_filter)

    if category:
        query = query.where(OpportunityIdea.category == category)
        count_query = count_query.where(OpportunityIdea.category == category)
    if region:
        query = query.where(OpportunityIdea.region == region)
        count_query = count_query.where(OpportunityIdea.region == region)
    if trend_type:
        query = query.where(OpportunityIdea.trend_type == trend_type)
        count_query = count_query.where(OpportunityIdea.trend_type == trend_type)
    if min_score is not None:
        query = query.where(OpportunityIdea.opportunity_score >= min_score)
        count_query = count_query.where(OpportunityIdea.opportunity_score >= min_score)
    if max_score is not None:
        query = query.where(OpportunityIdea.opportunity_score <= max_score)
        count_query = count_query.where(OpportunityIdea.opportunity_score <= max_score)
    if confidence_min is not None:
        query = query.where(OpportunityIdea.confidence_score >= confidence_min)
        count_query = count_query.where(OpportunityIdea.confidence_score >= confidence_min)
    if competition_max is not None:
        query = query.where(OpportunityIdea.competition_score <= competition_max)
        count_query = count_query.where(OpportunityIdea.competition_score <= competition_max)

    # Sort
    sort_col = SORT_COLUMNS[sort]
    query = query.order_by(sort_col.desc() if order == "desc" else sort_col.asc())

    # Pagination
    total = (await db.execute(count_query)).scalar() or 0
    offset = (page - 1) * limit
    query = query.offset(offset).limit(limit)

    result = await db.execute(query)
    items = result.scalars().all()

    response = PaginatedIdeas(
        items=[IdeaListItem.model_validate(i) for i in items],
        total=total,
        page=page,
        limit=limit,
        pages=math.ceil(total / limit) if total > 0 else 0,
    )
    await cache_set(cache_key, response.model_dump(), CACHE_TTL_SHORT)
    return response


@router.get("/{idea_id}", response_model=IdeaDetail)
async def get_idea(
    idea_id: int,
    db: AsyncSession = Depends(get_db),
    _user=Depends(get_current_user),
):
    result = await db.execute(
        select(OpportunityIdea)
        .options(selectinload(OpportunityIdea.cluster))
        .where(OpportunityIdea.id == idea_id)
    )
    idea = result.scalar_one_or_none()
    if not idea:
        raise HTTPException(status_code=404, detail="Idea not found")
    return IdeaDetail.model_validate(idea)


@router.get("/{idea_id}/related", response_model=list[IdeaListItem])
async def get_related_ideas(
    idea_id: int,
    db: AsyncSession = Depends(get_db),
    _user=Depends(get_current_user),
    limit: int = Query(5, ge=1, le=20),
):
    # Get the idea's cluster
    result = await db.execute(
        select(OpportunityIdea).where(OpportunityIdea.id == idea_id)
    )
    idea = result.scalar_one_or_none()
    if not idea or not idea.cluster_id:
        return []

    # Get other ideas in the same cluster
    result = await db.execute(
        select(OpportunityIdea)
        .where(
            OpportunityIdea.cluster_id == idea.cluster_id,
            OpportunityIdea.id != idea_id,
        )
        .order_by(OpportunityIdea.opportunity_score.desc())
        .limit(limit)
    )
    return [IdeaListItem.model_validate(i) for i in result.scalars().all()]
