from datetime import datetime

from pydantic import BaseModel


class SavedIdeaCreate(BaseModel):
    idea_id: int
    note: str | None = None


class SavedIdeaUpdate(BaseModel):
    note: str | None = None


class SavedIdeaResponse(BaseModel):
    id: int
    idea_id: int
    note: str | None
    created_at: datetime
    updated_at: datetime
    idea: "SavedIdeaIdeaInfo | None" = None

    model_config = {"from_attributes": True}


class SavedIdeaIdeaInfo(BaseModel):
    id: int
    title: str
    opportunity_score: float
    score_label: str | None
    category: str | None
    region: str | None

    model_config = {"from_attributes": True}


SavedIdeaResponse.model_rebuild()
