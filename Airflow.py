from datetime import datetime

from airflow import DAG
from airflow.decorators import task
from airflow.operators import PythonOperator

def say_hello():
    print("Hello, Airflow!")

with DAG(
    dag_id="hello_airflow",
    start_date=datetime(2025, 9, 10),
    schedule_interval="@daily",
    catchup=False
) as dag:
    task1 = PythonOperator(
        task_id="say_hello_task",
        python_callable=say_hello
    )