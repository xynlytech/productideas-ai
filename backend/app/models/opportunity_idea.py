from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.saved_idea import SavedIdea
    from app.models.topic_cluster import TopicCluster


class OpportunityIdea(Base):
    __tablename__ = "opportunity_ideas"

    id: Mapped[int] = mapped_column(primary_key=True)
    cluster_id: Mapped[int | None] = mapped_column(
        ForeignKey("topic_clusters.id"), index=True
    )
    title: Mapped[str] = mapped_column(String(500), index=True)
    problem_statement: Mapped[str | None] = mapped_column(Text)
    why_it_matters: Mapped[str | None] = mapped_column(Text)
    suggested_product: Mapped[str | None] = mapped_column(Text)
    category: Mapped[str | None] = mapped_column(String(100), index=True)
    region: Mapped[str | None] = mapped_column(String(100), index=True)
    trend_type: Mapped[str | None] = mapped_column(String(50))

    # Scores
    opportunity_score: Mapped[float] = mapped_column(Float, default=0.0, index=True)
    demand_growth_score: Mapped[float] = mapped_column(Float, default=0.0)
    competition_score: Mapped[float] = mapped_column(Float, default=0.0)
    pain_intensity_score: Mapped[float] = mapped_column(Float, default=0.0)
    confidence_score: Mapped[float] = mapped_column(Float, default=0.0)
    momentum_score: Mapped[float] = mapped_column(Float, default=0.0)
    query_volume: Mapped[int] = mapped_column(Integer, default=0)

    # Metadata
    score_label: Mapped[str | None] = mapped_column(String(50))
    ranking_reason: Mapped[str | None] = mapped_column(Text)
    confidence_caveats: Mapped[str | None] = mapped_column(Text)
    trend_data: Mapped[str | None] = mapped_column(Text)  # JSON serialized trend points
    signals_summary: Mapped[str | None] = mapped_column(Text)

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )

    cluster: Mapped[TopicCluster | None] = relationship(back_populates="ideas", lazy="selectin")
    saved_by: Mapped[list[SavedIdea]] = relationship(
        back_populates="idea", lazy="selectin", cascade="all, delete-orphan"
    )
