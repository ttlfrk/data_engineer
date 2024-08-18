"""Create Data Vault insert procedures

Revision ID: a581c98e6f2e
Revises:
Create Date: 2024-08-17 19:47:22.701418

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = 'a581c98e6f2e'
down_revision: str = 'b2f3dcf19b1d'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Функции для расчета hash_key для hubs
    op.execute('''
        CREATE FUNCTION data_vault.get_hub_course_hash_key(
            source_id   INTEGER,
            title       VARCHAR
        ) RETURNS UUID
        LANGUAGE SQL
            IMMUTABLE
            RETURN MD5(CONCAT(
                CAST(source_id AS VARCHAR),
                title
            ))::UUID
        ;
    ''')
    op.execute('''
        CREATE FUNCTION data_vault.get_hub_stream_hash_key(
            source_id      INTEGER,
            course_title   VARCHAR,
            stream_name    VARCHAR
        ) RETURNS UUID
        LANGUAGE SQL
            IMMUTABLE
            RETURN MD5(CONCAT(
                CAST(source_id AS VARCHAR),
                data_vault.get_hub_course_hash_key(
                    source_id,
                    course_title
                ),
                stream_name
            ))::UUID
        ;
    ''')
    op.execute('''
        CREATE FUNCTION data_vault.get_hub_stream_module_hash_key(
            source_id           INTEGER,
            course_title        VARCHAR,
            stream_name         VARCHAR,
            stream_module_title VARCHAR
        ) RETURNS UUID
        LANGUAGE SQL
            IMMUTABLE
            RETURN MD5(CONCAT(
                CAST(source_id AS VARCHAR),
                course_title,
                stream_name,
                stream_module_title
            ))::UUID
        ;
    ''')
    op.execute('''
        CREATE FUNCTION data_vault.get_hub_stream_module_lesson_hash_key(
            source_id           INTEGER,
            course_title        VARCHAR,
            stream_name         VARCHAR,
            stream_module_title VARCHAR,
            lesson_title        VARCHAR
        ) RETURNS UUID
        LANGUAGE SQL
            IMMUTABLE
            RETURN MD5(CONCAT(
                CAST(source_id AS VARCHAR),
                course_title,
                stream_name,
                stream_module_title,
                lesson_title
            ))::UUID
        ;
    ''')

    # Процедуры для обновления hubs
    op.execute('''
        CREATE OR REPLACE PROCEDURE data_vault.update_hub_course_from_source(
            loaded_at TIMESTAMP,
            source_id INTEGER
        )
        LANGUAGE plpgsql
        AS $$
        BEGIN
            INSERT INTO data_vault.hub_course (
                hash_key,
                loaded_at,
                source_id,
                course_id
            )
            SELECT
                data_vault.get_hub_course_hash_key(
                    source_id,
                    title
                ) AS hash_key,
                loaded_at AS load_date,
                source_id AS source_id,
                id AS course_id
            FROM
                source.course
            WHERE
                data_vault.get_hub_course_hash_key(
                    source_id,
                    title
                ) NOT IN (
                    SELECT
                        hash_key
                    FROM
                        data_vault.hub_course
                )
            ;
        END;
        $$
    ''')
    op.execute('''
        CREATE OR REPLACE PROCEDURE data_vault.update_hub_stream_from_source(
            loaded_at TIMESTAMP,
            source_id INTEGER
        )
        LANGUAGE plpgsql
        AS $$
        BEGIN
            INSERT INTO data_vault.hub_stream (
                hash_key,
                loaded_at,
                source_id,
                stream_id
            )
            SELECT
                data_vault.get_hub_stream_hash_key(
                    source_id,
                    course.title,
                    stream.name
                ) AS hash_key,
                loaded_at AS load_date,
                source_id AS source_id,
                stream.id AS stream_id
            FROM
                source.stream AS stream
            INNER JOIN source.course AS course ON
                course.id = stream.course_id
            WHERE
                data_vault.get_hub_stream_hash_key(
                    source_id,
                    course.title,
                    stream.name
                ) NOT IN (
                    SELECT
                        hash_key
                    FROM
                        data_vault.hub_stream
                )
            ;
        END;
        $$
    ''')
    op.execute('''
        CREATE OR REPLACE PROCEDURE data_vault.update_hub_stream_module_from_source(
            loaded_at TIMESTAMP,
            source_id INTEGER
        )
        LANGUAGE plpgsql
        AS $$
        BEGIN
            INSERT INTO data_vault.hub_stream_module (
                hash_key,
                loaded_at,
                source_id,
                stream_module_id
            )
            SELECT
                data_vault.get_hub_stream_module_hash_key(
                    source_id,
                    course.title,
                    stream.name,
                    stream_module.title
                ) AS hash_key,
                loaded_at AS load_date,
                source_id AS source_id,
                stream_module.id AS stream_module_id
            FROM
                source.stream_module AS stream_module
            INNER JOIN source.stream AS stream ON
                stream.id = stream_module.stream_id
            INNER JOIN source.course AS course ON
                course.id = stream.course_id
            WHERE
                data_vault.get_hub_stream_module_hash_key(
                    source_id,
                    course.title,
                    stream.name,
                    stream_module.title
                ) NOT IN (
                    SELECT
                        hash_key
                    FROM
                        data_vault.hub_stream_module
                )
            ;
        END;
        $$
    ''')  # noqa: E501
    op.execute('''
        CREATE OR REPLACE PROCEDURE data_vault.update_hub_stream_module_lesson_from_source(
            loaded_at TIMESTAMP,
            source_id INTEGER
        )
        LANGUAGE plpgsql
        AS $$
        BEGIN
            INSERT INTO data_vault.hub_stream_module_lesson (
                hash_key,
                loaded_at,
                source_id,
                stream_module_lesson_id
            )
            SELECT
                data_vault.get_hub_stream_module_lesson_hash_key(
                    source_id,
                    course.title,
                    stream.name,
                    stream_module.title,
                    stream_module_lesson.title
                ) AS hash_key,
                loaded_at AS load_date,
                source_id AS source_id,
                stream_module_lesson.id AS stream_module_lesson_id
            FROM
                source.stream_module_lesson AS stream_module_lesson
            INNER JOIN source.stream_module AS stream_module ON
                stream_module.id = stream_module_lesson.stream_module_id
            INNER JOIN source.stream AS stream ON
                stream.id = stream_module.stream_id
            INNER JOIN source.course AS course ON
                course.id = stream.course_id
            WHERE
                data_vault.get_hub_stream_module_lesson_hash_key(
                    source_id,
                    course.title,
                    stream.name,
                    stream_module.title,
                    stream_module_lesson.title
                ) NOT IN (
                    SELECT
                        hash_key
                    FROM
                        data_vault.hub_stream_module_lesson
                )
            ;
        END;
        $$
    ''')  # noqa: E501

    # Функции для расчета hask_key для links
    op.execute('''
        CREATE OR REPLACE FUNCTION data_vault.get_link_course_stream_hash_key(
            source_id    INTEGER,
            course_title VARCHAR,
            stream_name  VARCHAR
        ) RETURNS UUID
        LANGUAGE SQL
            IMMUTABLE
            RETURN MD5(CONCAT(
                CAST(data_vault.get_hub_course_hash_key(
                    source_id,
                    course_title
                ) AS VARCHAR),
                CAST(data_vault.get_hub_stream_hash_key(
                    source_id,
                    course_title,
                    stream_name
                ) AS VARCHAR)
            ))::UUID
        ;
    ''')
    op.execute('''
        CREATE OR REPLACE FUNCTION data_vault.get_link_stream_stream_module_hash_key(
            source_id             INTEGER,
            course_title          VARCHAR,
            stream_name           VARCHAR,
            stream_module_title   VARCHAR
        ) RETURNS UUID
        LANGUAGE SQL
            IMMUTABLE
            RETURN MD5(CONCAT(
                CAST(data_vault.get_hub_stream_hash_key(
                    source_id,
                    course_title,
                    stream_name
                ) AS VARCHAR),
                CAST(data_vault.get_hub_stream_module_hash_key(
                    source_id,
                    course_title,
                    stream_name,
                    stream_module_title
                ) AS VARCHAR)
            ))::UUID
        ;
    ''')  # noqa: E501
    op.execute('''
        CREATE OR REPLACE FUNCTION data_vault.get_link_stream_module_stream_module_lesson_hash_key(
            source_id                      INTEGER,
            course_title                   VARCHAR,
            stream_name                    VARCHAR,
            stream_module_title            VARCHAR,
            stream_module_lesson_title     VARCHAR
        ) RETURNS UUID
        LANGUAGE SQL
            IMMUTABLE
            RETURN MD5(CONCAT(
                CAST(data_vault.get_hub_stream_module_hash_key(
                    source_id,
                    course_title,
                    stream_name,
                    stream_module_title
                ) AS VARCHAR),
                CAST(data_vault.get_hub_stream_module_lesson_hash_key(
                    source_id,
                    course_title,
                    stream_name,
                    stream_module_title,
                    stream_module_lesson_title
                ) AS VARCHAR)
            ))::UUID
        ;
    ''')  # noqa: E501

    # Процедуры для обновления likns
    op.execute('''
        CREATE OR REPLACE PROCEDURE data_vault.update_link_course_stream_from_source(
            loaded_at TIMESTAMP,
            source_id INTEGER
        )
        LANGUAGE plpgsql
        AS $$
        BEGIN
            INSERT INTO data_vault.link_course_stream (
                hash_key,
                course_hash_key,
                stream_hash_key,
                loaded_at,
                source_id
            )
            SELECT
                data_vault.get_link_course_stream_hash_key(
                    source_id,
                    course.title,
                    stream.name
                ) AS hash_key,
                data_vault.get_hub_course_hash_key(
                    source_id,
                    course.title
                ) AS course_hash_key,
                data_vault.get_hub_stream_hash_key(
                    source_id,
                    course.title,
                    stream.name
                ) AS stream_hash_key,
                loaded_at AS loaded_at,
                source_id AS source_id
            FROM
                "source".course AS course
            INNER JOIN "source".stream AS stream ON
                stream.course_id = course.id
            WHERE
                data_vault.get_link_course_stream_hash_key(
                    source_id,
                    course.title,
                    stream.name
                ) NOT IN (
                    SELECT
                        hash_key
                    FROM
                        data_vault.link_course_stream
                )
            ;
        END;
        $$
    ''')  # noqa: E501
    op.execute('''
        CREATE OR REPLACE PROCEDURE data_vault.update_link_stream_stream_module_from_source(
            loaded_at TIMESTAMP,
            source_id INTEGER
        )
        LANGUAGE plpgsql
        AS $$
        BEGIN
            INSERT INTO data_vault.link_stream_stream_module (
                hash_key,
                stream_hash_key,
                stream_module_hash_key,
                loaded_at,
                source_id
            )
            SELECT
                data_vault.get_link_stream_stream_module_hash_key(
                    source_id,
                    course.title,
                    stream.name,
                    stream_module.title
                ) AS hash_key,
                data_vault.get_hub_stream_hash_key(
                    source_id,
                    course.title,
                    stream.name
                ) AS stream_hash_key,
                data_vault.get_hub_stream_module_hash_key(
                    source_id,
                    course.title,
                    stream.name,
                    stream_module.title
                ) AS stream_module_hash_key,
                loaded_at AS loaded_at,
                source_id AS source_id
            FROM
                "source".stream AS stream
            INNER JOIN "source".stream_module AS stream_module ON
                stream_module.stream_id = stream.id
            INNER JOIN "source".course AS course ON
                course.id = stream.course_id
            WHERE
                data_vault.get_link_stream_stream_module_hash_key(
                    source_id,
                    course.title,
                    stream.name,
                    stream_module.title
                ) NOT IN (
                    SELECT
                        hash_key
                    FROM
                        data_vault.link_stream_stream_module
                )
            ;
        END;
        $$
    ''')  # noqa: E501
    op.execute('''
        CREATE OR REPLACE PROCEDURE data_vault.update_link_stream_module_stream_module_lesson_from_source(
            loaded_at TIMESTAMP,
            source_id   INTEGER
        )
        LANGUAGE plpgsql
        AS $$
        BEGIN
            INSERT INTO data_vault.link_stream_module_stream_module_lesson (
                hash_key,
                stream_module_hash_key,
                stream_module_lesson_hash_key,
                loaded_at,
                source_id
            )
            SELECT
                data_vault.get_link_stream_module_stream_module_lesson_hash_key(
                    source_id,
                    course.title,
                    stream.name,
                    stream_module.title,
                    stream_module_lesson.title
                ) AS hash_key,
                data_vault.get_hub_stream_module_hash_key(
                    source_id,
                    course.title,
                    stream.name,
                    stream_module.title
                ) AS stream_module_hash_key,
                data_vault.get_hub_stream_module_lesson_hash_key(
                    source_id,
                    course.title,
                    stream.name,
                    stream_module.title,
                    stream_module_lesson.title
                ) AS stream_module_lesson_hash_key,
                loaded_at AS loaded_at,
                source_id AS source_id
            FROM
                "source".stream_module_lesson AS stream_module_lesson
            INNER JOIN "source".stream_module AS stream_module ON
                stream_module.id = stream_module_lesson.stream_module_id
            INNER JOIN "source".stream AS stream ON
                stream.id = stream_module.stream_id
            INNER JOIN "source".course AS course ON
                course.id = stream.course_id
            WHERE
                data_vault.get_link_stream_module_stream_module_lesson_hash_key(
                    source_id,
                    course.title,
                    stream.name,
                    stream_module.title,
                    stream_module_lesson.title
                ) NOT IN (
                    SELECT
                        hash_key
                    FROM
                        data_vault.link_stream_module_stream_module_lesson
                )
            ;
        END;
        $$
    ''')  # noqa: E501

    # Функции для расчета hask_key для sattelits (sat)
    op.execute('''
        CREATE OR REPLACE FUNCTION data_vault.get_sat_course_hash_key(
            title                  VARCHAR,
            icon_url               VARCHAR,
            is_auto_course_enroll  BOOLEAN,
            is_demo_enroll         BOOLEAN
        ) RETURNS UUID
        LANGUAGE SQL
            IMMUTABLE
            RETURN MD5(CONCAT(
                title,
                CAST(icon_url AS VARCHAR),
                CAST(is_auto_course_enroll AS VARCHAR),
                CAST(is_demo_enroll AS VARCHAR)
            ))::UUID
        ;
    ''')
    op.execute('''
        CREATE OR REPLACE FUNCTION data_vault.get_sat_stream_hash_key(
            start_at              TIMESTAMP,
            end_at                TIMESTAMP,
            is_open                 BOOLEAN,
            name                    VARCHAR,
            homework_deadline_days  INTEGER
        ) RETURNS UUID
        LANGUAGE SQL
            IMMUTABLE
            RETURN MD5(CONCAT(
                CAST(start_at AS VARCHAR),
                CAST(end_at AS VARCHAR),
                CAST(is_open AS VARCHAR),
                name,
                CAST(homework_deadline_days AS VARCHAR)
            ))::UUID
        ;
    ''')
    op.execute('''
        CREATE OR REPLACE FUNCTION data_vault.get_sat_stream_module_hash_key(
            title                 VARCHAR,
            order_in_stream       INTEGER
        ) RETURNS UUID
        LANGUAGE SQL
            IMMUTABLE
            RETURN MD5(CONCAT(
                title,
                CAST(order_in_stream AS VARCHAR)
            ))::UUID
        ;
    ''')
    op.execute('''
        CREATE OR REPLACE FUNCTION data_vault.get_sat_stream_module_lesson_hash_key(
            title                               VARCHAR,
            description                            TEXT,
            start_at                          TIMESTAMP,
            end_at                            TIMESTAMP,
            homework_url                        VARCHAR,
            teacher_id                          INTEGER,
            online_lesson_join_url              VARCHAR,
            online_lesson_recording_url         VARCHAR
        ) RETURNS UUID
        LANGUAGE SQL
            IMMUTABLE
            RETURN MD5(CONCAT(
                title,
                description,
                CAST(start_at AS VARCHAR),
                CAST(end_at AS VARCHAR),
                homework_url,
                CAST(teacher_id AS VARCHAR),
                online_lesson_join_url,
                online_lesson_recording_url
            ))::UUID
        ;
    ''')  # noqa: E501

    # Процедуры для обновления sattelits (sat)
    op.execute('''
        CREATE OR REPLACE PROCEDURE data_vault.update_sat_course_from_source(
            loaded_at TIMESTAMP,
            source_id INTEGER
        )
        LANGUAGE plpgsql
        AS $$
        BEGIN
            /* Обновляем записи на неактивные, которых нет в текущей базе */
            UPDATE
                data_vault.sat_course
            SET
                is_active = FALSE,
                end_active_date = LOCALTIMESTAMP
            WHERE
                hash_key NOT IN (
                    SELECT
                        data_vault.get_sat_course_hash_key(
                            title,
                            icon_url,
                            is_auto_course_enroll,
                            is_demo_enroll
                        )
                    FROM
                        "source".course
                )
                AND is_active
            ;
            /* Добавляем новые записи */
            INSERT INTO data_vault.sat_course (
                hash_key,
                course_hash_key,
                loaded_at,
                source_id,
                s_title,
                s_icon_url,
                s_is_auto_course_enroll,
                s_is_demo_enroll,
                start_active_date,
                end_active_date,
                is_active
            )
            SELECT
                data_vault.get_sat_course_hash_key(
                    title,
                    icon_url,
                    is_auto_course_enroll,
                    is_demo_enroll
                ) AS hash_key,
                data_vault.get_hub_course_hash_key(
                    source_id,
                    title
                ) AS course_hash_key,
                loaded_at AS loaded_at,
                source_id AS source_id,
                title,
                icon_url,
                is_auto_course_enroll,
                is_demo_enroll,
                created_at AS start_active_date,
                CASE
                    WHEN deleted_at IS NOT NULL
                    THEN deleted_at
                    ELSE '2099.01.01'::timestamp
                END AS end_active_date,
                deleted_at IS NULL AS is_active
            FROM
                "source".course
            WHERE
                data_vault.get_sat_course_hash_key(
                    title,
                    icon_url,
                    is_auto_course_enroll,
                    is_demo_enroll
                ) NOT IN (
                    SELECT
                        hash_key
                    FROM
                        data_vault.sat_course
                )
            ;
        END;
        $$
    ''')  # noqa: E501
    op.execute('''
        CREATE OR REPLACE PROCEDURE data_vault.update_sat_stream_from_source(
            loaded_at TIMESTAMP,
            source_id INTEGER
        )
        LANGUAGE plpgsql
        AS $$
        BEGIN
            /* Обновляем записи на неактивные, которых нет в текущей базе */
            UPDATE
                data_vault.sat_stream
            SET
                is_active = FALSE,
                end_active_date = LOCALTIMESTAMP
            WHERE
                hash_key NOT IN (
                    SELECT
                        data_vault.get_sat_stream_hash_key(
                            start_at,
                            end_at,
                            is_open,
                            name,
                            homework_deadline_days
                        )
                    FROM
                        "source".stream
                )
                AND is_active
            ;
            /* Добавляем новые записи */
            INSERT INTO data_vault.sat_stream (
                hash_key,
                stream_hash_key,
                loaded_at,
                source_id,
                s_start_at,
                s_end_at,
                s_is_open,
                s_name,
                s_homework_deadline_days,
                start_active_date,
                end_active_date,
                is_active
            )
            SELECT
                data_vault.get_sat_stream_hash_key(
                    stream.start_at,
                    stream.end_at,
                    stream.is_open,
                    stream.name,
                    stream.homework_deadline_days
                ) AS hash_key,
                data_vault.get_hub_stream_hash_key(
                    source_id,
                    course.title,
                    stream.name
                ) AS stream_hash_key,
                loaded_at AS loaded_at,
                source_id AS source_id,
                stream.start_at,
                stream.end_at,
                stream.is_open,
                stream.name,
                stream.homework_deadline_days,
                stream.created_at AS start_active_date,
                CASE
                    WHEN stream.deleted_at IS NOT NULL
                    THEN stream.deleted_at
                    ELSE '2099.01.01'::timestamp
                END AS end_active_date,
                stream.deleted_at IS NULL AS is_active
            FROM
                "source".stream AS stream
            INNER JOIN "source".course AS course ON
                course.id = stream.course_id
            WHERE
                data_vault.get_sat_stream_hash_key(
                    stream.start_at,
                    stream.end_at,
                    stream.is_open,
                    stream.name,
                    stream.homework_deadline_days
                ) NOT IN (
                    SELECT
                        hash_key
                    FROM
                        data_vault.sat_stream
                )
            ;
        END;
        $$
    ''')  # noqa: E501
    op.execute('''
        CREATE OR REPLACE PROCEDURE data_vault.update_sat_stream_module_from_source(
            loaded_at TIMESTAMP,
            source_id INTEGER
        )
        LANGUAGE plpgsql
        AS $$
        BEGIN
            /* Обновляем записи на неактивные, которых нет в текущей базе */
            UPDATE
                data_vault.sat_stream_module
            SET
                is_active = FALSE,
                end_active_date = LOCALTIMESTAMP
            WHERE
                hash_key NOT IN (
                    SELECT
                        data_vault.get_sat_stream_module_hash_key(
                            title,
                            order_in_stream
                        )
                    FROM
                        "source".stream_module
                )
                AND is_active
            ;
            /* Добавляем новые записи */
            INSERT INTO data_vault.sat_stream_module (
                hash_key,
                stream_module_hash_key,
                loaded_at,
                source_id,
                s_title,
                s_order_in_stream,
                start_active_date,
                end_active_date,
                is_active
            )
            SELECT
                data_vault.get_sat_stream_module_hash_key(
                    stream_module.title,
                    stream_module.order_in_stream
                ) AS hash_key,
                data_vault.get_hub_stream_module_hash_key(
                    source_id,
                    course.title,
                    stream.name,
                    stream_module.title
                ) AS stream_module_hash_key,
                loaded_at AS loaded_at,
                source_id AS source_id,
                stream_module.title,
                stream_module.order_in_stream,
                stream_module.created_at AS start_active_date,
                CASE
                    WHEN stream_module.deleted_at IS NOT NULL
                    THEN stream_module.deleted_at
                    ELSE '2099.01.01'::timestamp
                END AS end_active_date,
                stream_module.deleted_at IS NULL AS is_active
            FROM
                "source".stream_module AS stream_module
            INNER JOIN "source".stream AS stream ON
                stream.id = stream_module.stream_id
            INNER JOIN "source".course AS course ON
                course.id = stream.course_id
            WHERE
                data_vault.get_sat_stream_module_hash_key(
                    stream_module.title,
                    stream_module.order_in_stream
                ) NOT IN (
                    SELECT
                        hash_key
                    FROM
                        data_vault.sat_stream_module
                )
            ;
        END;
        $$
    ''')  # noqa: E501
    op.execute('''
        CREATE OR REPLACE PROCEDURE data_vault.update_sat_stream_module_lesson_from_source(
            loaded_at TIMESTAMP,
            source_id INTEGER
        )
        LANGUAGE plpgsql
        AS $$
        BEGIN
            /* Обновляем записи на неактивные, которых нет в текущей базе */
            UPDATE
                data_vault.sat_stream_module_lesson
            SET
                is_active = FALSE,
                end_active_date = LOCALTIMESTAMP
            WHERE
                hash_key NOT IN (
                    SELECT
                        data_vault.get_sat_stream_module_lesson_hash_key(
                            title,
                            description,
                            start_at,
                            end_at,
                            homework_url,
                            teacher_id,
                            online_lesson_join_url,
                            online_lesson_recording_url
                        )
                    FROM
                        "source".stream_module_lesson
                )
                AND is_active
            ;
            /* Добавляем новые записи */
            INSERT INTO data_vault.sat_stream_module_lesson (
                hash_key,
                stream_module_lesson_hash_key,
                loaded_at,
                source_id,
                s_title,
                s_description,
                s_start_at,
                s_end_at,
                s_homework_url,
                s_teacher_id,
                s_online_lesson_join_url,
                s_online_lesson_recording_url,
                start_active_date,
                end_active_date,
                is_active
            )
            SELECT
                data_vault.get_sat_stream_module_lesson_hash_key(
                    stream_module_lesson.title,
                    stream_module_lesson.description,
                    stream_module_lesson.start_at,
                    stream_module_lesson.end_at,
                    stream_module_lesson.homework_url,
                    stream_module_lesson.teacher_id,
                    stream_module_lesson.online_lesson_join_url,
                    stream_module_lesson.online_lesson_recording_url
                ) AS hash_key,
                data_vault.get_hub_stream_module_lesson_hash_key(
                    source_id,
                    course.title,
                    stream.name,
                    stream_module.title,
                    stream_module_lesson.title
                ) AS stream_module_lesson_hash_key,
                loaded_at AS loaded_at,
                source_id AS source_id,
                stream_module_lesson.title,
                stream_module_lesson.description,
                stream_module_lesson.start_at,
                stream_module_lesson.end_at,
                stream_module_lesson.homework_url,
                stream_module_lesson.teacher_id,
                stream_module_lesson.online_lesson_join_url,
                stream_module_lesson.online_lesson_recording_url,
                /* У занятия нет created_at, поэтому воруем
                 * дату создания у родителя - stream_module,
                 * т.к. ранее, чем он, урок не мог быть создан
                 */
                stream_module.created_at AS start_active_date,
                CASE
                    WHEN stream_module_lesson.deleted_at IS NOT NULL
                    THEN stream_module_lesson.deleted_at
                    ELSE '2099.01.01'::timestamp
                END AS end_active_date,
                stream_module_lesson.deleted_at IS NULL AS is_active
            FROM
                "source".stream_module_lesson AS stream_module_lesson
            INNER JOIN "source".stream_module AS stream_module ON
                stream_module.id = stream_module_lesson.stream_module_id
            INNER JOIN "source".stream AS stream ON
                stream.id = stream_module.stream_id
            INNER JOIN "source".course AS course ON
                course.id = stream.course_id
            WHERE
                data_vault.get_sat_stream_module_lesson_hash_key(
                    stream_module_lesson.title,
                    stream_module_lesson.description,
                    stream_module_lesson.start_at,
                    stream_module_lesson.end_at,
                    stream_module_lesson.homework_url,
                    stream_module_lesson.teacher_id,
                    stream_module_lesson.online_lesson_join_url,
                    stream_module_lesson.online_lesson_recording_url
                ) NOT IN (
                    SELECT
                        hash_key
                    FROM
                        data_vault.sat_stream_module_lesson
                )
            ;
        END;
        $$
    ''')  # noqa: E501

    # Процедура для обновления data_vault из источника 'source'
    op.execute('''
        CREATE OR REPLACE PROCEDURE data_vault.update_hubs()
        LANGUAGE plpgsql
        AS $$
        DECLARE
            source_id INTEGER;
            loaded_at TIMESTAMP := LOCALTIMESTAMP;
        BEGIN
            /* Заранее получаем source_id, избегая 100500 запросов */
            SELECT
                id
            INTO
                source_id
            FROM
                data_vault.sources
            WHERE
                name = 'source'
            LIMIT 1;
            /* Hub */
            CALL data_vault.update_hub_course_from_source(loaded_at, source_id);
            CALL data_vault.update_hub_stream_from_source(loaded_at, source_id);
            CALL data_vault.update_hub_stream_module_from_source(loaded_at, source_id);
            CALL data_vault.update_hub_stream_module_lesson_from_source(loaded_at, source_id);
            /* Link */
            CALL data_vault.update_link_course_stream_from_source(loaded_at, source_id);
            CALL data_vault.update_link_stream_stream_module_from_source(loaded_at, source_id);
            CALL data_vault.update_link_stream_module_stream_module_lesson_from_source(loaded_at, source_id);
            /* Settelite */
            CALL data_vault.update_sat_course_from_source(loaded_at, source_id);
            CALL data_vault.update_sat_stream_from_source(loaded_at, source_id);
            CALL data_vault.update_sat_stream_module_from_source(loaded_at, source_id);
            CALL data_vault.update_sat_stream_module_lesson_from_source(loaded_at, source_id);
        END;
        $$
    ''')  # noqa: E501


def downgrade() -> None:
    pass
