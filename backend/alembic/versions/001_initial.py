"""Initial migration - all tables

Revision ID: 001_initial
Revises:
Create Date: 2026-03-31
"""
from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

revision: str = "001_initial"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Users
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("email", sa.String(255), unique=True, nullable=False, index=True),
        sa.Column("hashed_password", sa.String(255), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("role", sa.String(50), nullable=False, server_default="user"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    # Topic Clusters
    op.create_table(
        "topic_clusters",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("label", sa.String(255), nullable=False, index=True),
        sa.Column("description", sa.Text()),
        sa.Column("category", sa.String(100), index=True),
        sa.Column("idea_count", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    # Cluster Keywords
    op.create_table(
        "cluster_keywords",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("cluster_id", sa.Integer(), sa.ForeignKey("topic_clusters.id"), nullable=False, index=True),
        sa.Column("keyword", sa.String(255), nullable=False, index=True),
        sa.Column("weight", sa.Float(), nullable=False, server_default=sa.text("1.0")),
        sa.Column("query_volume", sa.Integer()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    # Opportunity Ideas
    op.create_table(
        "opportunity_ideas",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("cluster_id", sa.Integer(), sa.ForeignKey("topic_clusters.id"), index=True),
        sa.Column("title", sa.String(500), nullable=False, index=True),
        sa.Column("problem_statement", sa.Text()),
        sa.Column("why_it_matters", sa.Text()),
        sa.Column("suggested_product", sa.Text()),
        sa.Column("category", sa.String(100), index=True),
        sa.Column("region", sa.String(100), index=True),
        sa.Column("trend_type", sa.String(50)),
        sa.Column("opportunity_score", sa.Float(), nullable=False, server_default=sa.text("0.0"), index=True),
        sa.Column("demand_growth_score", sa.Float(), nullable=False, server_default=sa.text("0.0")),
        sa.Column("competition_score", sa.Float(), nullable=False, server_default=sa.text("0.0")),
        sa.Column("pain_intensity_score", sa.Float(), nullable=False, server_default=sa.text("0.0")),
        sa.Column("confidence_score", sa.Float(), nullable=False, server_default=sa.text("0.0")),
        sa.Column("momentum_score", sa.Float(), nullable=False, server_default=sa.text("0.0")),
        sa.Column("query_volume", sa.Integer(), nullable=False, server_default=sa.text("0")),
        sa.Column("score_label", sa.String(50)),
        sa.Column("ranking_reason", sa.Text()),
        sa.Column("confidence_caveats", sa.Text()),
        sa.Column("trend_data", sa.Text()),
        sa.Column("signals_summary", sa.Text()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    # Source Signals
    op.create_table(
        "source_signals",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("source_type", sa.String(50), nullable=False, index=True),
        sa.Column("query", sa.String(500), nullable=False, index=True),
        sa.Column("region", sa.String(100)),
        sa.Column("language", sa.String(10)),
        sa.Column("raw_data", sa.JSON()),
        sa.Column("payload_ref", sa.String(500)),
        sa.Column("status", sa.String(50), nullable=False, server_default="raw"),
        sa.Column("ingested_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("processed_at", sa.DateTime(timezone=True)),
    )

    # Saved Ideas
    op.create_table(
        "saved_ideas",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False, index=True),
        sa.Column("idea_id", sa.Integer(), sa.ForeignKey("opportunity_ideas.id"), nullable=False, index=True),
        sa.Column("note", sa.Text()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    # Alerts
    op.create_table(
        "alerts",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False, index=True),
        sa.Column("keyword", sa.String(255)),
        sa.Column("category", sa.String(100)),
        sa.Column("region", sa.String(100)),
        sa.Column("min_score", sa.Float()),
        sa.Column("cadence", sa.String(50), nullable=False, server_default="daily"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("last_triggered_at", sa.DateTime(timezone=True)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    # Exports
    op.create_table(
        "exports",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=False, index=True),
        sa.Column("format", sa.String(10), nullable=False),
        sa.Column("status", sa.String(50), nullable=False, server_default="pending"),
        sa.Column("file_url", sa.String(500)),
        sa.Column("filters_used", sa.String(1000)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
        sa.Column("completed_at", sa.DateTime(timezone=True)),
    )

    # Audit Logs
    op.create_table(
        "audit_logs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), index=True),
        sa.Column("action", sa.String(100), nullable=False, index=True),
        sa.Column("resource_type", sa.String(100)),
        sa.Column("resource_id", sa.Integer()),
        sa.Column("details", sa.Text()),
        sa.Column("ip_address", sa.String(45)),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table("audit_logs")
    op.drop_table("exports")
    op.drop_table("alerts")
    op.drop_table("saved_ideas")
    op.drop_table("source_signals")
    op.drop_table("opportunity_ideas")
    op.drop_table("cluster_keywords")
    op.drop_table("topic_clusters")
    op.drop_table("users")
