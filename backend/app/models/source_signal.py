from datetime import UTC, datetime

from sqlalchemy import JSON, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class SourceSignal(Base):
    __tablename__ = "source_signals"

    id: Mapped[int] = mapped_column(primary_key=True)
    source_type: Mapped[str] = mapped_column(String(50), index=True)  # google_trends, autocomplete
    query: Mapped[str] = mapped_column(String(500), index=True)
    region: Mapped[str | None] = mapped_column(String(100))
    language: Mapped[str | None] = mapped_column(String(10))
    raw_data: Mapped[dict | None] = mapped_column(JSON)
    payload_ref: Mapped[str | None] = mapped_column(String(500))  # S3 key
    status: Mapped[str] = mapped_column(String(50), default="raw")  # raw, normalized, processed
    ingested_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )
    processed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
