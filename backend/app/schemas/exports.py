from datetime import datetime

from pydantic import BaseModel


class ExportCreate(BaseModel):
    format: str = "csv"  # csv or pdf
    filters: dict | None = None


class ExportResponse(BaseModel):
    id: int
    format: str
    status: str
    file_url: str | None
    created_at: datetime
    completed_at: datetime | None

    model_config = {"from_attributes": True}
