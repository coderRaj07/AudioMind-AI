"""add user password hash

Revision ID: 9b15d7c5b3d8
Revises: faaf32665530
Create Date: 2026-05-07 17:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "9b15d7c5b3d8"
down_revision: Union[str, None] = "faaf32665530"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("users", sa.Column("password_hash", sa.String(), nullable=True))


def downgrade() -> None:
    op.drop_column("users", "password_hash")
