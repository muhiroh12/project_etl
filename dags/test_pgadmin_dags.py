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
    'test_pgadmin', 
    schedule_interval='@once', 
    default_args=default_args, 
    catchup=False
    ) as dag:
    task_welcome = BashOperator(
        task_id ='say_welcome_pgadmin',
        bash_command = 'echo "Hallo !"'
    )
    create_table_bash = BashOperator(
        task_id='create_table',
        bash_command='python /opt/airflow/dags/script/airflow_retail_pgadmin.py'
    )

    task_end = BashOperator(
        task_id = 'say_end_pgadmin',
        bash_command = 'echo "Good Bye ..."'
    )

task_welcome >> create_table_bash >> task_end