from datetime import datetime

from pydantic import BaseModel


class AlertCreate(BaseModel):
    keyword: str | None = None
    category: str | None = None
    region: str | None = None
    min_score: float | None = None
    cadence: str = "daily"


class AlertUpdate(BaseModel):
    keyword: str | None = None
    category: str | None = None
    region: str | None = None
    min_score: float | None = None
    cadence: str | None = None
    is_active: bool | None = None


class AlertResponse(BaseModel):
    id: int
    keyword: str | None
    category: str | None
    region: str | None
    min_score: float | None
    cadence: str
    is_active: bool
    last_triggered_at: datetime | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
