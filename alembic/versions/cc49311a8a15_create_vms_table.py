"""create vms table

Revision ID: cc49311a8a15
Revises: 30e357373cbb
Create Date: 2024-10-14 13:19:50.419441

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'cc49311a8a15'
down_revision: Union[str, None] = '30e357373cbb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute('''
    create table vms (
        id varchar(255) primary key,
        resource_id varchar(255) not null,
        cpu_cores int not null,
        memory numeric(5, 2) not null,
        storage numeric(7, 2) not null,
        network_bandwidth numeric(7, 2) not null
    )
    ''')

def downgrade() -> None:
    op.execute('drop table vms')
