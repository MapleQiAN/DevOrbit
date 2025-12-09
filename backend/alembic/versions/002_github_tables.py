"""Add GitHub repo and daily stat tables

Revision ID: 002
Revises: 001
Create Date: 2025-12-09 11:50:21.953000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "002"
down_revision: Union[str, None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create GitHub repo and daily stat tables"""
    # Create github_repos table
    op.create_table(
        "github_repos",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("repo_id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("full_name", sa.String(length=255), nullable=False),
        sa.Column("private", sa.Boolean(), nullable=False),
        sa.Column("language", sa.String(length=100), nullable=True),
        sa.Column("html_url", sa.String(length=500), nullable=False),
        sa.Column("description", sa.String(length=1000), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("repo_id"),
    )
    op.create_index(op.f("ix_github_repos_full_name"), "github_repos", ["full_name"], unique=False)
    op.create_index(op.f("ix_github_repos_id"), "github_repos", ["id"], unique=False)
    op.create_index(op.f("ix_github_repos_repo_id"), "github_repos", ["repo_id"], unique=True)
    op.create_index(op.f("ix_github_repos_user_id"), "github_repos", ["user_id"], unique=False)

    # Create github_daily_stats table
    op.create_table(
        "github_daily_stats",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("date", sa.Date(), nullable=False),
        sa.Column("commit_count", sa.Integer(), nullable=False),
        sa.Column("pr_count", sa.Integer(), nullable=False),
        sa.Column("issue_count", sa.Integer(), nullable=False),
        sa.Column("star_delta", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_github_daily_stats_date"), "github_daily_stats", ["date"], unique=False)
    op.create_index(op.f("ix_github_daily_stats_id"), "github_daily_stats", ["id"], unique=False)
    op.create_index(op.f("ix_github_daily_stats_user_id"), "github_daily_stats", ["user_id"], unique=False)


def downgrade() -> None:
    """Drop GitHub tables"""
    op.drop_index(op.f("ix_github_daily_stats_user_id"), table_name="github_daily_stats")
    op.drop_index(op.f("ix_github_daily_stats_id"), table_name="github_daily_stats")
    op.drop_index(op.f("ix_github_daily_stats_date"), table_name="github_daily_stats")
    op.drop_table("github_daily_stats")
    
    op.drop_index(op.f("ix_github_repos_user_id"), table_name="github_repos")
    op.drop_index(op.f("ix_github_repos_repo_id"), table_name="github_repos")
    op.drop_index(op.f("ix_github_repos_id"), table_name="github_repos")
    op.drop_index(op.f("ix_github_repos_full_name"), table_name="github_repos")
    op.drop_table("github_repos")

