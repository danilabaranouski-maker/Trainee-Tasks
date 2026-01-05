import os
from airflow import DAG
from airflow.sensors.python import PythonSensor
from airflow.operators.trigger_dagrun import TriggerDagRunOperator
from airflow.operators.python import PythonOperator
from airflow.utils.dates import days_ago

from airline_utils import archive_file_func, CSV_FILE_PATH, ARCHIVE_DIR

default_args = {
    'owner': 'airflow',
    'start_date': days_ago(1),
}

def check_file_exists():
    exists = os.path.exists(CSV_FILE_PATH)
    if exists:
        print(f"File found at {CSV_FILE_PATH}!")
    else:
        print(f"Waiting for file at {CSV_FILE_PATH}...")
    return exists

with DAG(
    '00_airline_master_orchestrator',
    default_args=default_args,
    schedule_interval='*/10 * * * *', 
    catchup=False,
    max_active_runs=1 
) as dag:

    wait_for_file = PythonSensor(
        task_id='wait_for_csv_file',
        python_callable=check_file_exists,
        poke_interval=30,
        timeout=60 * 10,
        mode='poke'
    )

    trigger_raw = TriggerDagRunOperator(
        task_id='trigger_raw_layer',
        trigger_dag_id='02_airline_raw_layer',
        wait_for_completion=True,
        poke_interval=20
    )

    trigger_target = TriggerDagRunOperator(
        task_id='trigger_target_layer',
        trigger_dag_id='03_airline_target_layer',
        wait_for_completion=True,
        poke_interval=20
    )

    trigger_marts = TriggerDagRunOperator(
        task_id='trigger_marts_layer',
        trigger_dag_id='04_airline_marts_layer',
        wait_for_completion=True,
        poke_interval=20
    )

    archive_file = PythonOperator(
        task_id='archive_processed_file',
        python_callable=archive_file_func,
        op_kwargs={
            'source_path': CSV_FILE_PATH,
            'archive_dir': ARCHIVE_DIR
        }
    )

    wait_for_file >> trigger_raw >> trigger_target >> trigger_marts >> archive_file