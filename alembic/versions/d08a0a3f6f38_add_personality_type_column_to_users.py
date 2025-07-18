"""add personality_type column to users

Revision ID: d08a0a3f6f38
Revises: 660f1bf1e1ef
Create Date: 2025-07-04 20:47:08.715538

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "d08a0a3f6f38"
down_revision: Union[str, None] = "660f1bf1e1ef"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("users", sa.Column("personality_type", sa.String(length=100), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column("users", "personality_type")
    # ### end Alembic commands ###
