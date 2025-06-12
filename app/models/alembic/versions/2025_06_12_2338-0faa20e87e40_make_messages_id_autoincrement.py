"""make messages id autoincrement

Revision ID: 0faa20e87e40
Revises: 4868c393361c
Create Date: 2025-06-12 23:38:27.105406+00:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '0faa20e87e40'
down_revision: Union[str, None] = '4868c393361c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column('messages', 'id',
                    existing_type=sa.BigInteger(),
                    type_=sa.BigInteger(),
                    existing_nullable=False,
                    autoincrement=True,
                    existing_server_default=sa.text("nextval('chats_id_seq'::regclass)"))


def downgrade() -> None:
    op.alter_column('messages', 'id',
                    existing_type=sa.BigInteger(),
                    type_=sa.BIGINT(),
                    existing_nullable=False,
                    existing_server_default=sa.text("nextval('chats_id_seq'::regclass)"))
