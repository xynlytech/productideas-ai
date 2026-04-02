from __future__ import annotations

from datetime import UTC, datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base

if TYPE_CHECKING:
    from app.models.topic_cluster import TopicCluster


class ClusterKeyword(Base):
    __tablename__ = "cluster_keywords"

    id: Mapped[int] = mapped_column(primary_key=True)
    cluster_id: Mapped[int] = mapped_column(ForeignKey("topic_clusters.id"), index=True)
    keyword: Mapped[str] = mapped_column(String(255), index=True)
    weight: Mapped[float] = mapped_column(Float, default=1.0)
    query_volume: Mapped[int | None] = mapped_column(Integer)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(UTC)
    )

    cluster: Mapped[TopicCluster] = relationship(back_populates="keywords")
