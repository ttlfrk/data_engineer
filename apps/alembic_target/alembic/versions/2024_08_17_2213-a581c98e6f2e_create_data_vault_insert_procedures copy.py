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
    op.execute('''
        CREATE OR REPLACE PROCEDURE data_vault.update_hub_cource_from_source(
            loaded_at TIMESTAMP
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
                MD5(CAST(id AS varchar))::uuid AS hash_key,
                loaded_at AS load_date,
                (
                    SELECT
                        id
                    FROM
                        data_vault.sources
                    WHERE
                        name = 'source'
                    LIMIT 1
                ) AS source_id,
                id AS course_id
            FROM
                source.course
            WHERE
                MD5(CAST(id AS varchar))::uuid NOT IN (
                    SELECT
                        hash_key
                    FROM
                        data_vault.hub_course
                );
        END;
        $$
    ''')
    op.execute('''
        CREATE OR REPLACE PROCEDURE data_vault.update_hub_stream_from_source(
            loaded_at TIMESTAMP
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
                MD5(CAST(id AS varchar))::uuid AS hash_key,
                loaded_at AS load_date,
                (
                    SELECT
                        id
                    FROM
                        data_vault.sources
                    WHERE
                        name = 'source'
                    LIMIT 1
                ) AS source_id,
                id AS stream_id
            FROM
                source.stream
            WHERE
                MD5(CAST(id AS varchar))::uuid NOT IN (
                    SELECT
                        hash_key
                    FROM
                        data_vault.hub_stream
                );
        END;
        $$
    ''')
    op.execute('''
        CREATE OR REPLACE PROCEDURE data_vault.update_hub_stream_module_from_source(
            loaded_at TIMESTAMP
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
                MD5(CAST(id AS varchar))::uuid AS hash_key,
                loaded_at AS load_date,
                (
                    SELECT
                        id
                    FROM
                        data_vault.sources
                    WHERE
                        name = 'source'
                    LIMIT 1
                ) AS source_id,
                id AS stream_module_id
            FROM
                source.stream_module
            WHERE
                MD5(CAST(id AS varchar))::uuid NOT IN (
                    SELECT
                        hash_key
                    FROM
                        data_vault.hub_stream_module
                );
        END;
        $$
    ''')  # noqa: E501

    op.execute('''
        CREATE OR REPLACE PROCEDURE data_vault.update_hubs()
        LANGUAGE plpgsql
        AS $$
        DECLARE
            source_id INTEGER;
            loaded_at TIMESTAMP := LOCALTIMESTAMP;
        BEGIN
            CALL data_vault.update_hub_cource_from_source(loaded_at);
            CALL data_vault.update_hub_stream_from_source(loaded_at);
            CALL data_vault.update_hub_stream_module_from_source(loaded_at);
        END;
        $$
    ''')


def downgrade() -> None:
    pass
