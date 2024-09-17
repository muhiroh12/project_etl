from airflow import DAG
from airflow.operators.python import PythonOperator
from datetime import datetime,timedelta
from pandasql import sqldf
from sqlalchemy import create_engine
import pandas as pd


default_args = {
    "owner": "Muhii",
    "start_date": datetime(2024, 7, 21),
    "depends_on_past": False,
    "email_on_failure": False,
    "email_on_retry": False,
    "email": "muhii.smta@gmail.com",
    "retries": 1,
    "retry_delay": timedelta(minutes=5)
}

def db_connection():
    return create_engine( 'postgresql+psycopg2://airflow:airflow@localhost:5434/test_database')

def etl_data():
    engine = db_connection()
    TABLE_NAME = 'test_customer'
    #get data from csv file
    df = pd.read_csv('/opt/airflow/dags/input/customer_info.csv')
    df = df.loc[:, ~df.columns.str.contains('^Unnamed')]
    filtered_df=df[df['country'] == 'Australia'].copy()

    #transform process
    #df_idn = sqldf(''' select * from df where country='Australia' ''')

    #jumlah record yang akan di save ke table
    count_data = filtered_df.shape[0]

    #load data after transformation to postgresql
    with engine.begin() as connection:
        filtered_df.to_sql(name=TABLE_NAME, con=connection,index=False,if_exists='append')
        print(f'Total Record has been inserted are {count_data} to table {TABLE_NAME} ')

def welcome():
    print('Welcome to Apache Airflow')
    print('First run this task then execute task transform_csv and transform_json parallel')
    print('Then finally run task end_task')

def end_task():
    print('This task is executed after run task welcome, transform_csv and trans- form_json')
    print('End')

with DAG('test_load_database', schedule_interval="@once", default_args=default_args, catchup=False) as dag:
    task_welcome = PythonOperator(task_id='say_welcome', python_callable=welcome)
    task_etl = PythonOperator(task_id='task_etl', python_callable=etl_data)
    task_end = PythonOperator(task_id='say_end', python_callable=end_task)
    
task_welcome >> task_etl >> task_end