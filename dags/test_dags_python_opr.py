from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime,timedelta
import pandas as pd

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

def etl_data():
    df = pd.read_csv('/opt/airflow/dags/input/customer_info.csv')
    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
    filtered_df=df[df['country'] == 'Australia']
    filtered_df.to_csv('/opt/airflow/dags/output/test_output.csv', index=False)

def welcome():
    print('Welcome to Apache Airflow')
    print('First run this task then execute task transform_csv and transform_json parallel')
    print('Then finally run task end_task')

def end_task():
    print('This task is executed after run task welcome, transform_csv and trans- form_json')
    print('End')

with DAG('etl_green_trip_data_python_opr',
         schedule_interval="@once",
         default_args=default_args,
         catchup=False
         ) as dag:
    task_welcome = PythonOperator(task_id='say_welcome', python_callable=welcome)
    task_etl = PythonOperator(task_id='task_etl', python_callable=etl_data)
    task_end = PythonOperator(task_id='say_end', python_callable=end_task)

task_welcome >> task_etl >> task_end