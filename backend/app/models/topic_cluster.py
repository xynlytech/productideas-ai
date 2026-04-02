from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.cluster_keyword import ClusterKeyword
    from app.models.opportunity_idea import OpportunityIdea


class TopicCluster(Base):
    __tablename__ = "topic_clusters"

    id: Mapped[int] = mapped_column(primary_key=True)
    label: Mapped[str] = mapped_column(String(255), index=True)
    description: Mapped[str | None] = mapped_column(Text)
    category: Mapped[str | None] = mapped_column(String(100), index=True)
    idea_count: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(UTC),
        onupdate=lambda: datetime.now(UTC),
    )

    keywords: Mapped[list[ClusterKeyword]] = relationship(
        back_populates="cluster", lazy="selectin", cascade="all, delete-orphan"
    )
    ideas: Mapped[list[OpportunityIdea]] = relationship(
        back_populates="cluster", lazy="selectin"
    )
