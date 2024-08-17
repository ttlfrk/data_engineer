import datetime

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook


SELECT__SOURCE_COURSE = '''
SELECT
    id,
    title,
    created_at,
    updated_at,
    deleted_at,
    icon_url,
    is_auto_course_enroll,
    is_demo_enroll
FROM
    course
WHERE
    created_at >= %(last_updated_at)s
    OR updated_at >= %(last_updated_at)s
    OR deleted_at >= %(last_updated_at)s
'''

SELECT__SOURCE_STREAM = '''
SELECT
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
FROM
    stream
WHERE
    created_at >= %(last_updated_at)s
    OR updated_at >= %(last_updated_at)s
'''

SELECT__SOURCE_STREAM_MODULE = '''
SELECT
    id,
    stream_id,
    title,
    created_at,
    updated_at,
    order_in_stream,
    deleted_at
FROM
    stream_module
WHERE
    created_at >= %(last_updated_at)s
    OR updated_at >= %(last_updated_at)s
    OR deleted_at >= %(last_updated_at)s
'''


def move_data(
    target_table_name: str,
    source_select: str,
) -> None:
    # Получаем соединение к target
    target = PostgresHook('DB_TARGET')
    target_conn = target.get_conn()
    target_conn_cursor = target_conn.cursor()

    # Находим последний loaded_at
    target_conn_cursor.execute('''
        SELECT
            COALESCE(
                MAX(loaded_at),
                '1970.01.01'::timestamp
            ) AS LAST_LOADED_AT
        FROM
            data_vault.hub_%s
    ''' % target_table_name)
    last_updated_at = target_conn_cursor.fetchone()[0]

    # Получаем соединение к source
    source = PostgresHook('DB_SOURCE')
    source_conn = source.get_conn()
    source_conn_cursor = source_conn.cursor()

    # Копируем данные из source в target
    source_conn_cursor.execute(
        query=source_select,
        vars=dict(
            last_updated_at=last_updated_at,
        ),
    )
    target_conn_cursor.executemany(
        'CALL source.insert_%s(%s)' % (
            target_table_name,
            ', '.join(['%s'] * len(source_conn_cursor.description))
        ),
        source_conn_cursor,
    )
    target_conn.commit()


with DAG(
    dag_id='export_data_from_source_to_target',
    start_date=datetime.datetime(2024, 8, 15),
    schedule="@once",
    catchup=False,
) as dag:
    task_copy_source_course = PythonOperator(
        task_id='copy_source_course',
        python_callable=move_data,
        op_kwargs=dict(
            target_table_name='course',
            source_select=SELECT__SOURCE_COURSE,
        ),
    )
    task_copy_source_stream = PythonOperator(
        task_id='copy_source_stream',
        python_callable=move_data,
        op_kwargs=dict(
            target_table_name='stream',
            source_select=SELECT__SOURCE_STREAM,
        ),
    )
    task_copy_source_stream_module = PythonOperator(
        task_id='copy_source_stream_module',
        python_callable=move_data,
        op_kwargs=dict(
            target_table_name='stream_module',
            source_select=SELECT__SOURCE_STREAM_MODULE,
        ),
    )
    task_update_hubs = SQLExecuteQueryOperator(
        task_id='task_update_hubs',
        sql="CALL data_vault.update_hubs()",
        conn_id='DB_TARGET',
    )

    task_copy_source_course >> \
        task_copy_source_stream >> \
        task_copy_source_stream_module >> \
        task_update_hubs
