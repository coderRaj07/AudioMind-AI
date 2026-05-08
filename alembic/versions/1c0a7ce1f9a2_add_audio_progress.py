"""add audio progress

Revision ID: 1c0a7ce1f9a2
Revises: faaf32665530
Create Date: 2026-05-08 18:30:00.000000
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1c0a7ce1f9a2'
down_revision: Union[str, None] = '9b15d7c5b3d8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('audios', sa.Column('progress', sa.Float(), nullable=False, server_default='0.0'))


def downgrade() -> None:
    op.drop_column('audios', 'progress')
