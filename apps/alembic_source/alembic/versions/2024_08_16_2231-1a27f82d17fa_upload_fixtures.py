"""Upload fixtures

Revision ID: 1a27f82d17fa
Revises:
Create Date: 2024-08-16 22:31:01.081421

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = '1a27f82d17fa'
down_revision: str = 'd06c18f34055'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None
table_names = [
    'course',
    'stream',
    'stream_module',
    'stream_module_lesson',
]
fixtures_path = '/usr/src/fixtures/%s.csv'


def upgrade() -> None:
    for table_name in table_names:
        with open(fixtures_path % table_name, 'r', newline='') as file:
            conn = op.get_bind().connection
            cursor = conn.cursor()
            cmd = "COPY %s FROM STDIN WITH (FORMAT CSV, HEADER TRUE)"
            cursor.copy_expert(cmd % table_name, file)
            conn.commit()


def downgrade() -> None:
    op.execute('TRUNCATE TABLE %s' % (
        ', '.join(table_names)
    ))
