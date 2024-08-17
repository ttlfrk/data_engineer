"""Init basic tables

Revision ID: d06c18f34055
Revises:
Create Date: 2024-08-16 18:15:07.007628

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = 'd06c18f34055'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create table course
    op.execute('''
        CREATE TABLE course (
            id                          INTEGER PRIMARY KEY,
            title                  VARCHAR(255),
            created_at                TIMESTAMP,
            updated_at                TIMESTAMP,
            deleted_at             TIMESTAMP(0),
            icon_url               VARCHAR(255),
            is_auto_course_enroll       BOOLEAN,
            is_demo_enroll              BOOLEAN
        );
    ''')
    op.execute('''
        COMMENT ON TABLE course IS 'Профессия/курс, который изучают на потоке';
    ''')

    # Create table stream
    op.execute('''
        CREATE TABLE stream (
            id                           INTEGER PRIMARY KEY,
            course_id                    INTEGER REFERENCES course(id),
            start_at                   TIMESTAMP,
            end_at                     TIMESTAMP,
            created_at                 TIMESTAMP,
            updated_at                 TIMESTAMP,
            deleted_at                 TIMESTAMP,
            is_open                      BOOLEAN,
            name                    VARCHAR(255),
            homework_deadline_days       INTEGER
        );
    ''')
    op.execute('''
        COMMENT ON TABLE stream IS 'Поток - группа студентов';
    ''')

    # Create table stream_module
    op.execute('''
        CREATE TABLE stream_module (
            id                       INTEGER PRIMARY KEY,
            stream_id                INTEGER REFERENCES stream(id),
            title               VARCHAR(255),
            created_at             TIMESTAMP,
            updated_at             TIMESTAMP,
            order_in_stream          INTEGER,
            deleted_at             TIMESTAMP
        );
    ''')
    op.execute('''
        COMMENT ON TABLE stream_module IS 'Модули, которые входят в состав курса/профессии';
    ''')  # noqa: E501

    # Create table stream_module_lesson
    op.execute('''
        CREATE TABLE stream_module_lesson (
            id                                 INTEGER PRIMARY KEY,
            title                         VARCHAR(255),
            description                           TEXT,
            start_at                         TIMESTAMP,
            end_at                           TIMESTAMP,
            homework_url                  VARCHAR(500),
            teacher_id                         INTEGER,
            stream_module_id                   INTEGER REFERENCES stream_module(id),
            deleted_at                    TIMESTAMP(0),
            online_lesson_join_url        VARCHAR(255),
            online_lesson_recording_url   VARCHAR(255)
        );
    ''')  # noqa: E501
    op.execute('''
        COMMENT ON TABLE stream_module_lesson IS 'Уроки, которые входят в модули';
    ''')  # noqa: E501


def downgrade() -> None:
    pass
