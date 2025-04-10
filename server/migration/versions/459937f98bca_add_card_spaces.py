"""add card spaces

Revision ID: 459937f98bca
Revises: 4b4308e3ef8e
Create Date: 2025-04-07 12:28:23.884245

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '459937f98bca'
down_revision: Union[str, None] = '4b4308e3ef8e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('card', sa.Column('limit', sa.Integer(), nullable=True))
    op.add_column('card', sa.Column('last_transaction', sa.DateTime(), nullable=True))
    op.add_column('card', sa.Column('transactions', sa.ARRAY(sa.String()), nullable=True))
    op.add_column('card', sa.Column('last_bank_touch', sa.DateTime(), nullable=True))
    op.alter_column('card', 'cvv',
               existing_type=sa.INTEGER(),
               nullable=False)
    op.alter_column('card', 'pin',
               existing_type=sa.INTEGER(),
               nullable=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('card', 'pin',
               existing_type=sa.INTEGER(),
               nullable=True)
    op.alter_column('card', 'cvv',
               existing_type=sa.INTEGER(),
               nullable=True)
    op.drop_column('card', 'last_bank_touch')
    op.drop_column('card', 'transactions')
    op.drop_column('card', 'last_transaction')
    op.drop_column('card', 'limit')
    # ### end Alembic commands ###
