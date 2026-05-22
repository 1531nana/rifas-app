"""initial schema

Revision ID: 20260521_0001
Revises:
Create Date: 2026-05-21 19:00:00.000000
"""

from alembic import op
import sqlalchemy as sa
import sqlmodel

revision = "20260521_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "admin",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("email", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("password_hash", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("full_name", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_admin_email"), "admin", ["email"], unique=True)
    op.create_table(
        "raffle",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("admin_id", sa.Integer(), nullable=False),
        sa.Column("name", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("lottery_type", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("total_numbers", sa.Integer(), nullable=False),
        sa.Column("ticket_price", sa.Integer(), nullable=False),
        sa.Column("prize_description", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("draw_date", sa.DateTime(), nullable=False),
        sa.Column("prize_image_url", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("public_token", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("status", sa.Enum("active", "closed", name="rafflestatus"), nullable=False),
        sa.Column("winner_number", sa.Integer(), nullable=True),
        sa.Column("winner_registered_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["admin_id"], ["admin.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_raffle_admin_id"), "raffle", ["admin_id"], unique=False)
    op.create_index(op.f("ix_raffle_public_token"), "raffle", ["public_token"], unique=True)
    op.create_table(
        "reservation",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("raffle_id", sa.Integer(), nullable=False),
        sa.Column("number", sa.Integer(), nullable=False),
        sa.Column("buyer_name", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("buyer_phone", sqlmodel.sql.sqltypes.AutoString(), nullable=False),
        sa.Column("buyer_email", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("payment_method", sa.Enum("card", "pse", "cash", name="paymentmethod"), nullable=False),
        sa.Column("status", sa.Enum("pending", "paid", "expired", "cancelled", name="reservationstatus"), nullable=False),
        sa.Column("expires_at", sa.DateTime(), nullable=False),
        sa.Column("paid_at", sa.DateTime(), nullable=True),
        sa.Column("wompi_transaction_id", sqlmodel.sql.sqltypes.AutoString(), nullable=True),
        sa.Column("reminder_sent_at", sa.DateTime(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["raffle_id"], ["raffle.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_reservation_number"), "reservation", ["number"], unique=False)
    op.create_index(op.f("ix_reservation_raffle_id"), "reservation", ["raffle_id"], unique=False)
    op.create_index(op.f("ix_reservation_status"), "reservation", ["status"], unique=False)
    op.create_index(op.f("ix_reservation_wompi_transaction_id"), "reservation", ["wompi_transaction_id"], unique=False)
    op.create_index(
        "ux_active_reservation_number",
        "reservation",
        ["raffle_id", "number"],
        unique=True,
        postgresql_where=sa.text("status IN ('pending', 'paid')"),
        sqlite_where=sa.text("status IN ('pending', 'paid')"),
    )


def downgrade() -> None:
    op.drop_index("ux_active_reservation_number", table_name="reservation")
    op.drop_index(op.f("ix_reservation_wompi_transaction_id"), table_name="reservation")
    op.drop_index(op.f("ix_reservation_status"), table_name="reservation")
    op.drop_index(op.f("ix_reservation_raffle_id"), table_name="reservation")
    op.drop_index(op.f("ix_reservation_number"), table_name="reservation")
    op.drop_table("reservation")
    op.drop_index(op.f("ix_raffle_public_token"), table_name="raffle")
    op.drop_index(op.f("ix_raffle_admin_id"), table_name="raffle")
    op.drop_table("raffle")
    op.drop_index(op.f("ix_admin_email"), table_name="admin")
    op.drop_table("admin")
