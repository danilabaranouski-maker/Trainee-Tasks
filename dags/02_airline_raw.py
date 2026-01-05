from airflow import DAG
from airflow.providers.snowflake.operators.snowflake import SnowflakeOperator
from airflow.operators.python import PythonOperator
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
from airline_utils import DEFAULT_ARGS, read_sql, upload_to_stage_func

with DAG(
    dag_id='02_airline_raw_layer', 
    default_args=DEFAULT_ARGS, 
    schedule_interval=None, 
    catchup=False,
    tags=['airline', 'layer_2_raw']
) as dag:
    upload_file = PythonOperator(
        task_id='upload_file_to_stage',
        python_callable=upload_to_stage_func
    )

    create_raw_table = SnowflakeOperator(
        task_id='create_raw_table_ddl',
        sql=read_sql('02_create_raw.sql'),
        warehouse='COMPUTE_WH',
        database='AIRLINE_DWH',
        role='ACCOUNTADMIN'
    )

    load_raw_data = SnowflakeOperator(
        task_id='load_raw_data_dml',
        sql=read_sql('03_load_raw.sql'),
        warehouse='COMPUTE_WH',
        database='AIRLINE_DWH',
        role='ACCOUNTADMIN'
    )

    upload_file >> create_raw_table >> load_raw_data