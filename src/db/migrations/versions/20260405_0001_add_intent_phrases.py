"""Add intent_phrases table

Revision ID: a1b2c3d4e5f6
Revises: 31d369a74c32
Create Date: 2026-04-05 00:01:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "a1b2c3d4e5f6"
down_revision = "31d369a74c32"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # intenttype enum is already created by the initial migration — reference only.
    intenttype = postgresql.ENUM(
        "INFORMATIONAL", "COMMERCIAL", "NAVIGATIONAL", "TRANSACTIONAL",
        name="intenttype",
        create_type=False,
    )
    op.create_table(
        "intent_phrases",
        sa.Column("id", sa.Integer(), autoincrement=True, nullable=False),
        sa.Column("website_id", sa.Integer(), nullable=True),
        sa.Column("intent", intenttype, nullable=False),
        sa.Column("phrase", sa.String(length=500), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(
            ["website_id"],
            ["websites.id"],
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_intent_phrases_website_id"),
        "intent_phrases",
        ["website_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_intent_phrases_intent"),
        "intent_phrases",
        ["intent"],
        unique=False,
    )
    op.create_index(
        "ix_intent_phrases_website_intent",
        "intent_phrases",
        ["website_id", "intent"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_intent_phrases_website_intent", table_name="intent_phrases")
    op.drop_index(op.f("ix_intent_phrases_intent"), table_name="intent_phrases")
    op.drop_index(op.f("ix_intent_phrases_website_id"), table_name="intent_phrases")
    op.drop_table("intent_phrases")
    # Do NOT drop intenttype enum — it is shared with other tables.
