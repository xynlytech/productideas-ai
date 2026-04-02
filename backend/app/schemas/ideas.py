from datetime import datetime

from pydantic import BaseModel


class KeywordResponse(BaseModel):
    id: int
    keyword: str
    weight: float
    query_volume: int | None

    model_config = {"from_attributes": True}


class ClusterResponse(BaseModel):
    id: int
    label: str
    description: str | None
    category: str | None
    idea_count: int
    keywords: list[KeywordResponse]
    created_at: datetime

    model_config = {"from_attributes": True}


class ClusterListResponse(BaseModel):
    id: int
    label: str
    category: str | None
    idea_count: int
    created_at: datetime

    model_config = {"from_attributes": True}


class ScoreBreakdown(BaseModel):
    demand_growth: float
    competition: float
    pain_intensity: float
    confidence: float
    momentum: float
    query_volume: int


class IdeaListItem(BaseModel):
    id: int
    title: str
    problem_statement: str | None
    category: str | None
    region: str | None
    trend_type: str | None
    opportunity_score: float
    score_label: str | None
    demand_growth_score: float
    confidence_score: float
    momentum_score: float
    query_volume: int
    created_at: datetime

    model_config = {"from_attributes": True}


class IdeaDetail(BaseModel):
    id: int
    title: str
    problem_statement: str | None
    why_it_matters: str | None
    suggested_product: str | None
    category: str | None
    region: str | None
    trend_type: str | None
    opportunity_score: float
    score_label: str | None
    demand_growth_score: float
    competition_score: float
    pain_intensity_score: float
    confidence_score: float
    momentum_score: float
    query_volume: int
    ranking_reason: str | None
    confidence_caveats: str | None
    trend_data: str | None
    signals_summary: str | None
    cluster: ClusterListResponse | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class PaginatedIdeas(BaseModel):
    items: list[IdeaListItem]
    total: int
    page: int
    limit: int
    pages: int
