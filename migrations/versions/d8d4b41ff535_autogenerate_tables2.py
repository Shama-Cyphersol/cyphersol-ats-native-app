"""Autogenerate tables2

Revision ID: d8d4b41ff535
Revises: 898820a62dd5
Create Date: 2024-12-05 17:49:30.155503

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'd8d4b41ff535'
down_revision: Union[str, None] = '898820a62dd5'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('statements', 'end_date')
    op.drop_column('statements', 'start_date')
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('statements', sa.Column('start_date', sa.DATE(), nullable=False))
    op.add_column('statements', sa.Column('end_date', sa.DATE(), nullable=False))
    # ### end Alembic commands ###