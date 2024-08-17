import datetime

from airflow import DAG
from airflow.providers.common.sql.operators.sql import SQLExecuteQueryOperator


with DAG(
    dag_id='export_data_from_source_to_target',
    start_date=datetime.datetime(2024, 8, 15),
    schedule="@once",
    catchup=False,
) as dag:
    create_pet_table = SQLExecuteQueryOperator(
        task_id="select_nothing",
        sql='SELECT 1',
        conn_id='DB_SOURCE',
    )
