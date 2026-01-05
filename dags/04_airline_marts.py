from airflow import DAG
from airflow.providers.snowflake.operators.snowflake import SnowflakeOperator
from airline_utils import DEFAULT_ARGS, read_sql

with DAG(
    dag_id='04_airline_marts_layer', 
    default_args=DEFAULT_ARGS, 
    schedule_interval=None, 
    catchup=False,
    tags=['airline', 'layer_4_marts']
) as dag:
    
    create_view = SnowflakeOperator(
        task_id='create_secure_view',
        sql=read_sql('06_create_marts.sql'),
        warehouse='COMPUTE_WH',
        database='AIRLINE_DWH',
        role='ACCOUNTADMIN'
    )

    create_view