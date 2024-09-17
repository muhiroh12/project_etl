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

with DAG('customer_product_bash', schedule_interval=None, default_args=default_args, catchup=False) as dag:
    task_welcome = BashOperator(
        task_id ='say_welcome',
        bash_command = 'echo "Hallo !"'
    )
    task_process_etl = BashOperator(
        task_id='retailDataWithAirflow',
        bash_command='python /opt/airflow/dags/script/retailDataWithAirflow.py'
    )
    task_end = BashOperator(
        task_id = 'say_end',
        bash_command = 'echo "Good Bye ..."'
    )

task_welcome >> task_process_etl >> task_end