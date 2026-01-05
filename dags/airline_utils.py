from airflow.providers.snowflake.hooks.snowflake import SnowflakeHook
from airflow.utils.dates import days_ago
import os
import shutil
from datetime import datetime

# --- НАСТРОЙКИ ПУТЕЙ ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__)) 
SQL_DIR = os.path.join(BASE_DIR, 'sql')
DATA_DIR = os.path.join(BASE_DIR, 'data') 
CSV_FILE_PATH = os.path.join(DATA_DIR, 'Airline Dataset.csv')
ARCHIVE_DIR = os.path.join(DATA_DIR, 'archive') # Папка для архива

DEFAULT_ARGS = {
    'owner': 'airflow',
    'start_date': days_ago(1),
    'retries': 0,
    'snowflake_conn_id': 'snowflake_default',
}

def read_sql(filename):
    path = os.path.join(SQL_DIR, filename)
    if not os.path.exists(path):
        raise FileNotFoundError(f"Could not find SQL file: {path}")
    with open(path, 'r') as file:
        return file.read()

def upload_to_stage_func(file_path=None, stage_name=None):
    target_file = file_path if file_path else CSV_FILE_PATH
    target_stage = stage_name if stage_name else 'AIRLINE_DWH.RAW_DATA.MY_INTERNAL_STAGE'

    if not os.path.exists(target_file):
        raise Exception(f"File not found at: {target_file}")
    
    print(f"Found file: {target_file}, size: {os.path.getsize(target_file)}")

    hook = SnowflakeHook(snowflake_conn_id='snowflake_default')
    conn = hook.get_conn()
    cursor = conn.cursor()
    try:
        print(f"Uploading {target_file} to Snowflake Stage {target_stage}...")
        sql = f"PUT 'file://{target_file}' @{target_stage} AUTO_COMPRESS=TRUE OVERWRITE=TRUE"
        cursor.execute(sql)
        
        for row in cursor.fetchall():
            print(f"Upload status: {row}")
            if row[6] != 'UPLOADED' and row[6] != 'SKIPPED':
                 raise Exception(f"Upload failed: {row[6]}")
    finally:
        cursor.close()
        conn.close()

def archive_file_func(source_path=None, archive_dir=None):
    src = source_path if source_path else CSV_FILE_PATH
    dst_dir = archive_dir if archive_dir else ARCHIVE_DIR

    if not os.path.exists(src):
        print(f"File {src} not found, nothing to archive.")
        return

    if not os.path.exists(dst_dir):
        os.makedirs(dst_dir)

    filename = os.path.basename(src) 
    name, ext = os.path.splitext(filename)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    new_filename = f"{name}_{timestamp}{ext}"
    
    destination_path = os.path.join(dst_dir, new_filename)

    shutil.move(src, destination_path)
    print(f"File moved to: {destination_path}")