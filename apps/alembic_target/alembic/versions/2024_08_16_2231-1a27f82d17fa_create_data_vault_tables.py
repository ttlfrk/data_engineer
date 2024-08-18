"""Create Data Vault tables

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
    op.execute('CREATE SCHEMA data_vault')

    # Create table sources
    op.execute('''
        CREATE TABLE data_vault.sources (
            id            SERIAL PRIMARY KEY,
            name     VARCHAR(50) NOT NULL
        );
        COMMENT ON TABLE data_vault.sources IS 'Справочник источников';
        INSERT INTO data_vault.sources (
            name
        ) VALUES (
            'source'
        );
    ''')

    # Create hub tables
    op.execute('''
        CREATE TABLE data_vault.hub_course (
            hash_key                       UUID NOT NULL PRIMARY KEY,
            loaded_at                 TIMESTAMP NOT NULL DEFAULT now(),
            source_id                   INTEGER NOT NULL REFERENCES data_vault.sources(id),
            course_id                   INTEGER NOT NULL
        );
        COMMENT ON TABLE data_vault.hub_course IS 'Хаб для курсов';
    ''')  # noqa: E501
    op.execute('''
        CREATE TABLE data_vault.hub_stream (
            hash_key                       UUID NOT NULL PRIMARY KEY,
            loaded_at                 TIMESTAMP NOT NULL DEFAULT now(),
            source_id                   INTEGER NOT NULL REFERENCES data_vault.sources(id),
            stream_id                   INTEGER NOT NULL
        );
        COMMENT ON TABLE data_vault.hub_stream IS 'Хаб для потоков';
    ''')  # noqa: E501
    op.execute('''
        CREATE TABLE data_vault.hub_stream_module (
            hash_key                       UUID NOT NULL PRIMARY KEY,
            loaded_at                 TIMESTAMP NOT NULL DEFAULT now(),
            source_id                   INTEGER NOT NULL REFERENCES data_vault.sources(id),
            stream_module_id            INTEGER NOT NULL
        );
        COMMENT ON TABLE data_vault.hub_stream_module IS 'Хаб для модулей потока';
    ''')  # noqa: E501
    op.execute('''
        CREATE TABLE data_vault.hub_stream_module_lesson (
            hash_key                       UUID NOT NULL PRIMARY KEY,
            loaded_at                 TIMESTAMP NOT NULL DEFAULT now(),
            source_id                   INTEGER NOT NULL REFERENCES data_vault.sources(id),
            stream_module_lesson_id     INTEGER NOT NULL
        );
        COMMENT ON TABLE data_vault.hub_stream_module_lesson IS 'Хаб для уроков модуля';
    ''')  # noqa: E501

    # Create link tables
    op.execute('''
        CREATE TABLE data_vault.link_course_stream (
            hash_key                           UUID NOT NULL PRIMARY KEY,
            course_hash_key                    UUID NOT NULL REFERENCES data_vault.hub_course(hash_key),
            stream_hash_key                    UUID NOT NULL REFERENCES data_vault.hub_stream(hash_key),
            loaded_at                     TIMESTAMP NOT NULL DEFAULT now(),
            source_id                       INTEGER NOT NULL REFERENCES data_vault.sources(id)
        );
        COMMENT ON TABLE data_vault.link_course_stream IS 'Линк для связи курса и потока';
    ''')  # noqa: E501
    op.execute('''
        CREATE TABLE data_vault.link_stream_stream_module (
            hash_key                           UUID NOT NULL PRIMARY KEY,
            stream_hash_key                    UUID NOT NULL REFERENCES data_vault.hub_stream(hash_key),
            stream_module_hash_key             UUID NOT NULL REFERENCES data_vault.hub_stream_module(hash_key),
            loaded_at                     TIMESTAMP NOT NULL DEFAULT now(),
            source_id                       INTEGER NOT NULL REFERENCES data_vault.sources(id)
        );
        COMMENT ON TABLE data_vault.link_stream_stream_module IS 'Линк для связи потока и модулей';
    ''')  # noqa: E501
    op.execute('''
        CREATE TABLE data_vault.link_stream_module_stream_module_lesson (
            hash_key                           UUID NOT NULL PRIMARY KEY,
            stream_module_hash_key             UUID NOT NULL REFERENCES data_vault.hub_stream_module(hash_key),
            stream_module_lesson_hash_key      UUID NOT NULL REFERENCES data_vault.hub_stream_module_lesson(hash_key),
            loaded_at                     TIMESTAMP NOT NULL DEFAULT now(),
            source_id                       INTEGER NOT NULL REFERENCES data_vault.sources(id)
        );
        COMMENT ON TABLE data_vault.link_stream_module_stream_module_lesson IS 'Линк для уроков и модулей';
    ''')  # noqa: E501

    # Create sattelits
    op.execute('''
        CREATE TABLE data_vault.sat_course (
            hash_key                                 UUID NOT NULL,
            course_hash_key                          UUID NOT NULL REFERENCES data_vault.hub_course(hash_key),
            loaded_at                           TIMESTAMP NOT NULL DEFAULT now(),
            source_id                             INTEGER NOT NULL REFERENCES data_vault.sources(id),
            s_title                            VARCHAR(255),
            s_icon_url                         VARCHAR(255),
            s_is_auto_course_enroll                 BOOLEAN,
            s_is_demo_enroll                        BOOLEAN,
            start_active_date                     TIMESTAMP NOT NULL,
            end_active_date                       TIMESTAMP NOT NULL,
            is_active                               BOOLEAN NOT NULL,
            PRIMARY KEY(hash_key, course_hash_key)
        );
        COMMENT ON TABLE data_vault.sat_course IS 'Саттелит для курса';
    ''')  # noqa: E501
    op.execute('''
        CREATE TABLE data_vault.sat_stream (
            hash_key                                 UUID NOT NULL,
            stream_hash_key                          UUID NOT NULL REFERENCES data_vault.hub_stream(hash_key),
            loaded_at                           TIMESTAMP NOT NULL DEFAULT now(),
            source_id                             INTEGER NOT NULL REFERENCES data_vault.sources(id),
            s_start_at                          TIMESTAMP,
            s_end_at                            TIMESTAMP,
            s_is_open                             BOOLEAN,
            s_name                           VARCHAR(255),
            s_homework_deadline_days              INTEGER,
            start_active_date                   TIMESTAMP NOT NULL,
            end_active_date                     TIMESTAMP NOT NULL,
            is_active                             BOOLEAN NOT NULL,
            PRIMARY KEY(hash_key, stream_hash_key)
        );
        COMMENT ON TABLE data_vault.sat_stream IS 'Саттелит для потока';
    ''')  # noqa: E501
    op.execute('''
        CREATE TABLE data_vault.sat_stream_module (
            hash_key                                 UUID NOT NULL,
            stream_module_hash_key                   UUID NOT NULL REFERENCES data_vault.hub_stream_module(hash_key),
            loaded_at                           TIMESTAMP NOT NULL DEFAULT now(),
            source_id                             INTEGER NOT NULL REFERENCES data_vault.sources(id),
            s_title                          VARCHAR(255),
            s_order_in_stream                     INTEGER,
            start_active_date                   TIMESTAMP NOT NULL,
            end_active_date                     TIMESTAMP NOT NULL,
            is_active                             BOOLEAN NOT NULL,
            PRIMARY KEY(hash_key, stream_module_hash_key)
        );
        COMMENT ON TABLE data_vault.sat_stream_module IS 'Саттелит для модуля';
    ''')  # noqa: E501
    op.execute('''
        CREATE TABLE data_vault.sat_stream_module_lesson (
            hash_key                                 UUID NOT NULL,
            stream_module_lesson_hash_key            UUID NOT NULL REFERENCES data_vault.hub_stream_module_lesson(hash_key),
            loaded_at                           TIMESTAMP NOT NULL DEFAULT now(),
            source_id                             INTEGER NOT NULL REFERENCES data_vault.sources(id),
            s_title                          VARCHAR(255),
            s_description                            TEXT,
            s_start_at                          TIMESTAMP,
            s_end_at                            TIMESTAMP,
            s_homework_url                   VARCHAR(500),
            s_teacher_id                          INTEGER,
            s_online_lesson_join_url         VARCHAR(255),
            s_online_lesson_recording_url    VARCHAR(255),
            start_active_date                   TIMESTAMP NOT NULL,
            end_active_date                     TIMESTAMP NOT NULL,
            is_active                             BOOLEAN NOT NULL,
            PRIMARY KEY(hash_key, stream_module_lesson_hash_key)
        );
        COMMENT ON TABLE data_vault.sat_stream_module_lesson IS 'Саттелит для урока';
    ''')  # noqa: E501


def downgrade() -> None:
    op.execute('''
        DROP TABLE IF EXISTS
            data_vault.sat_stream_module_lesson,
            data_vault.sat_stream_module,
            data_vault.sat_stream,
            data_vault.sat_course,
            data_vault.link_stream_module_stream_module_lesson,
            data_vault.link_stream_stream_module,
            data_vault.link_course_stream,
            data_vault.hub_stream_module_lesson,
            data_vault.hub_stream_module,
            data_vault.hub_stream,
            data_vault.hub_course,
            data_vault.sources
        CASCADE;
        DROP SCHEMA data_vault;
    ''')
