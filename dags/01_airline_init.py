from airflow import DAG
from airflow.providers.snowflake.operators.snowflake import SnowflakeOperator
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
from airline_utils import DEFAULT_ARGS, read_sql

with DAG(
    dag_id='01_airline_init_infra', 
    default_args=DEFAULT_ARGS, 
    schedule_interval=None, 
    catchup=False,
    tags=['airline', 'layer_1_init']
) as dag:
    
    init_db_schema = SnowflakeOperator(
        task_id='init_db_schema_stage',
        sql=read_sql('01_init_infra.sql'),
        warehouse='COMPUTE_WH',
        role='ACCOUNTADMIN'
    )

    init_db_schema