from airflow import DAG
from airflow.providers.snowflake.operators.snowflake import SnowflakeOperator
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
from airline_utils import DEFAULT_ARGS, read_sql

with DAG(
    dag_id='03_airline_target_layer', 
    default_args=DEFAULT_ARGS, 
    schedule_interval=None, 
    catchup=False,
    tags=['airline', 'layer_3_target']
) as dag:
    
    create_target_tables = SnowflakeOperator(
        task_id='create_target_tables_ddl',
        sql=read_sql('04_create_target.sql'),
        warehouse='COMPUTE_WH',
        database='AIRLINE_DWH',
        role='ACCOUNTADMIN'
    )

    transform_data = SnowflakeOperator(
        task_id='transform_data_dml',
        sql=read_sql('05_transform_target.sql'),
        warehouse='COMPUTE_WH',
        database='AIRLINE_DWH',
        role='ACCOUNTADMIN'
    )

    create_target_tables >> transform_data