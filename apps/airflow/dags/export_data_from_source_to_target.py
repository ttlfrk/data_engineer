import datetime

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator
from airflow.providers.postgres.hooks.postgres import PostgresHook


# ---------------------------
# Запросы SOURCE для выгрузки
# ---------------------------

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
    created_at > %(filter_value)s
    OR updated_at > %(filter_value)s
    OR deleted_at > %(filter_value)s
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
    created_at > %(filter_value)s
    OR updated_at > %(filter_value)s
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
    created_at > %(filter_value)s
    OR updated_at > %(filter_value)s
    OR deleted_at > %(filter_value)s
'''

SELECT__SOURCE_STREAM_MODULE_LESSON = '''
SELECT
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
FROM
    stream_module_lesson
WHERE
    id > %(filter_value)s
'''

# ---------------------------
# Запросы для фильтрации
# ---------------------------

SELECT__FILTER_QUERY__LOADED_AT = '''
    SELECT
        COALESCE(
            MAX(loaded_at),
            '1970.01.01'::timestamp
        ) AS LAST_LOADED_AT
    FROM
        data_vault.hub_%s
'''

SELECT__FILTER_QUERY__MAX_ID = '''
    SELECT
        COALESCE(
            MAX(id),
            0
        ) AS MAX_ID
    FROM
        source.%s
'''


def move_data(
    target_table_name: str,
    source_select: str,
    filter_query: str,
) -> None:
    # Получаем соединение к target
    target = PostgresHook('DB_TARGET')
    target_conn = target.get_conn()
    target_conn_cursor = target_conn.cursor()

    # Находим значение для фильтрации
    target_conn_cursor.execute(filter_query % target_table_name)
    filter_value = target_conn_cursor.fetchone()[0]

    # Получаем соединение к source
    source = PostgresHook('DB_SOURCE')
    source_conn = source.get_conn()
    source_conn_cursor = source_conn.cursor()

    # Копируем данные из source в target
    source_conn_cursor.execute(
        query=source_select,
        vars=dict(
            filter_value=filter_value,
        ),
    )
    # У каждой функции/запроса разное кол-во
    # столбцов, поэтому, генерируем подстановку
    # значений по кол-ву столбцов из ответа
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
            filter_query=SELECT__FILTER_QUERY__LOADED_AT,
        ),
    )
    task_copy_source_stream = PythonOperator(
        task_id='copy_source_stream',
        python_callable=move_data,
        op_kwargs=dict(
            target_table_name='stream',
            source_select=SELECT__SOURCE_STREAM,
            filter_query=SELECT__FILTER_QUERY__LOADED_AT,
        ),
    )
    task_copy_source_stream_module = PythonOperator(
        task_id='copy_source_stream_module',
        python_callable=move_data,
        op_kwargs=dict(
            target_table_name='stream_module',
            source_select=SELECT__SOURCE_STREAM_MODULE,
            filter_query=SELECT__FILTER_QUERY__LOADED_AT,
        ),
    )
    # У уроков (stream_module_lesson) нет возможности
    # инкрементально выгружать (кроме max(id))
    task_copy_source_stream_module_lesson = PythonOperator(
        task_id='copy_source_stream_module_lesson',
        python_callable=move_data,
        op_kwargs=dict(
            target_table_name='stream_module_lesson',
            source_select=SELECT__SOURCE_STREAM_MODULE_LESSON,
            filter_query=SELECT__FILTER_QUERY__MAX_ID,
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
        task_copy_source_stream_module_lesson >> \
        task_update_hubs
