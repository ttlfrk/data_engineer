"""Create source insert procedures

Revision ID: b2f3dcf19b1d
Revises:
Create Date: 2024-08-17 19:47:22.701418

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = 'b2f3dcf19b1d'
down_revision: str = '1a27f82d17fa'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute('''
        CREATE OR REPLACE PROCEDURE source.insert_course(
            id                      INTEGER,
            title                   VARCHAR,
            created_at            TIMESTAMP,
            updated_at            TIMESTAMP,
            deleted_at            TIMESTAMP,
            icon_url                VARCHAR,
            is_auto_course_enroll   BOOLEAN,
            is_demo_enroll          BOOLEAN
        )
        LANGUAGE SQL
        AS
        $$
            INSERT INTO source.course (
                id,
                title,
                created_at,
                updated_at,
                deleted_at,
                icon_url,
                is_auto_course_enroll,
                is_demo_enroll
            )
            VALUES (
                id,
                title,
                created_at,
                updated_at,
                deleted_at,
                icon_url,
                is_auto_course_enroll,
                is_demo_enroll
            ) ON CONFLICT (id) DO UPDATE SET
                title = EXCLUDED.title,
                created_at = EXCLUDED.created_at,
                updated_at = EXCLUDED.updated_at,
                deleted_at = EXCLUDED.deleted_at,
                icon_url = EXCLUDED.icon_url,
                is_auto_course_enroll = EXCLUDED.is_auto_course_enroll,
                is_demo_enroll = EXCLUDED.is_demo_enroll;
        $$
    ''')
    op.execute('''
        CREATE OR REPLACE PROCEDURE source.insert_stream(
            id                          INTEGER,
            course_id                   INTEGER,
            start_at                  TIMESTAMP,
            end_at                    TIMESTAMP,
            created_at                TIMESTAMP,
            updated_at                TIMESTAMP,
            deleted_at                TIMESTAMP,
            is_open                     BOOLEAN,
            "name"                      VARCHAR,
            homework_deadline_days      INTEGER
        )
        LANGUAGE SQL
        AS
        $$
            INSERT INTO source.stream (
                id,
                course_id,
                start_at,
                end_at,
                created_at,
                updated_at,
                deleted_at,
                is_open,
                "name",
                homework_deadline_days
            )
            VALUES (
                id,
                course_id,
                start_at,
                end_at,
                created_at,
                updated_at,
                deleted_at,
                is_open,
                "name",
                homework_deadline_days
            ) ON CONFLICT (id) DO UPDATE SET
                id = EXCLUDED.id,
                course_id = EXCLUDED.course_id,
                start_at = EXCLUDED.start_at,
                end_at = EXCLUDED.end_at,
                created_at = EXCLUDED.created_at,
                updated_at = EXCLUDED.updated_at,
                deleted_at = EXCLUDED.deleted_at,
                is_open = EXCLUDED.is_open,
                "name" = EXCLUDED."name",
                homework_deadline_days = EXCLUDED.homework_deadline_days;
        $$
    ''')
    op.execute('''
        CREATE OR REPLACE PROCEDURE source.insert_stream_module(
            id                       INTEGER,
            stream_id                INTEGER,
            title                    VARCHAR,
            created_at             TIMESTAMP,
            updated_at             TIMESTAMP,
            order_in_stream          INTEGER,
            deleted_at             TIMESTAMP
        )
        LANGUAGE SQL
        AS
        $$
            INSERT INTO source.stream_module (
                id,
                stream_id,
                title,
                created_at,
                updated_at,
                order_in_stream,
                deleted_at
            )
            VALUES (
                id,
                stream_id,
                title,
                created_at,
                updated_at,
                order_in_stream,
                deleted_at
            ) ON CONFLICT (id) DO UPDATE SET
                id = EXCLUDED.id,
                stream_id = EXCLUDED.stream_id,
                title = EXCLUDED.title,
                created_at = EXCLUDED.created_at,
                updated_at = EXCLUDED.updated_at,
                order_in_stream = EXCLUDED.order_in_stream,
                deleted_at = EXCLUDED.deleted_at;
        $$
    ''')
    op.execute('''
        CREATE OR REPLACE PROCEDURE source.insert_stream_module_lesson(
            id                                 INTEGER,
            title                              VARCHAR,
            description                           TEXT,
            start_at                         TIMESTAMP,
            end_at                           TIMESTAMP,
            homework_url                       VARCHAR,
            teacher_id                         INTEGER,
            stream_module_id                   INTEGER,
            deleted_at                       TIMESTAMP,
            online_lesson_join_url             VARCHAR,
            online_lesson_recording_url        VARCHAR
        )
        LANGUAGE SQL
        AS
        $$
            INSERT INTO source.stream_module_lesson (
                id,
                title,
                description,
                start_at,
                end_at,
                homework_url,
                teacher_id,
                stream_module_id,
                deleted_at,
                online_lesson_join_url,
                online_lesson_recording_url
            )
            VALUES (
                id,
                title,
                description,
                start_at,
                end_at,
                homework_url,
                teacher_id,
                stream_module_id,
                deleted_at,
                online_lesson_join_url,
                online_lesson_recording_url
            ) ON CONFLICT (id) DO UPDATE SET
                id = EXCLUDED.id,
                title = EXCLUDED.title,
                description = EXCLUDED.description,
                start_at = EXCLUDED.start_at,
                end_at = EXCLUDED.end_at,
                homework_url = EXCLUDED.homework_url,
                teacher_id = EXCLUDED.teacher_id,
                stream_module_id = EXCLUDED.stream_module_id,
                deleted_at = EXCLUDED.deleted_at,
                online_lesson_join_url = EXCLUDED.online_lesson_join_url,
                online_lesson_recording_url = EXCLUDED.online_lesson_recording_url;
        $$
    ''')  # noqa: E501


def downgrade() -> None:
    pASs
