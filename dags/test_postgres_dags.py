from airflow import DAG
from datetime import datetime,timedelta
from airflow.operators.bash import BashOperator

default_args = {
    "owner": "Muhii",
    "start_date": datetime(2024, 9, 9),
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
    "email": "muhii.smta@gmail.com",
    "retries": 1,
    "retry_delay": timedelta(minutes=5)
}

with DAG(
    'test_postgres', 
    schedule_interval='@once', 
    default_args=default_args, 
    catchup=False
    ) as dag:
    task_welcome = BashOperator(
        task_id ='say_welcome_postgres',
        bash_command = 'echo "Hallo !"'
    )
    task_process_etl = BashOperator(
        task_id='testPostgres',
        bash_command='python /opt/airflow/dags/script/testpostgres.py'
    )
    task_end = BashOperator(
        task_id = 'say_end_postgres',
        bash_command = 'echo "Good Bye ..."'
    )

task_welcome >> task_process_etl >> task_end