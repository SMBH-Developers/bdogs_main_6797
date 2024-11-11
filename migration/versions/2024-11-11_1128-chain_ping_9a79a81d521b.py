"""chain_ping

Revision ID: 9a79a81d521b
Revises: 2f5fb5854640
Create Date: 2024-11-11 11:28:41.834619

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '9a79a81d521b'
down_revision: Union[str, None] = '2f5fb5854640'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('users', sa.Column('ping_step', sa.String(length=16), nullable=True))
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_column('users', 'ping_step')
    # ### end Alembic commands ###
