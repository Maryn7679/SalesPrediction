import textwrap
from datetime import datetime, timedelta
from airflow.providers.standard.operators.bash import BashOperator
from airflow.providers.standard.operators.python import PythonOperator
from airflow.sdk import DAG


def extract():
    return


def validate():
    return


def transform():
    return


def load():
    return


def quality_check():
    return


with DAG(
    "pipeline",
) as dag:
    extract = PythonOperator(
        task_id="extract",
        python_callable=extract
    ),
    validate = PythonOperator(
        task_id="validate",
        python_callable=validate
    ),
    transform = PythonOperator(
        task_id="transform",
        python_callable=transform
    ),
    load = PythonOperator(
        task_id="load",
        python_callable=load
    ),
    quality_check = PythonOperator(
        task_id="quality_check",
        python_callable=quality_check
    )

    extract >> [validate, quality_check] >> transform >> load
