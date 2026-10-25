import os
import pandas as pd
from airflow.sdk import task
from airflow.providers.standard.operators.bash import BashOperator
from airflow.providers.standard.operators.python import PythonOperator
from airflow.sdk import DAG


data = pd.DataFrame()


def extract():
    os.system('dvc pull')

    global data
    data = pd.read_csv("Data/blinkit_orders.csv", sep=';')

    return "dvc data pulled"


def validate():
    global data

    if not {'order_id', 'customer_id', 'order_date', 'promised_delivery_time',
            'actual_delivery_time', 'delivery_status', 'order_total', 'payment_method',
            'delivery_partner_id', 'store_id'}.issubset(data.columns):
        raise Exception("Data is missing required columns")
    return


def transform():
    global data

    data = data[["order_id", "customer_id", "order_date", "order_total"]]
    return


def load():
    global data

    old_data = pd.read_csv("Data/Features/blinkit_orders_features.csv", sep=';')
    data = pd.merge(old_data, data, "outer", on="order_id")

    data.to_csv("Data/Features/blinkit_orders_features.csv", sep=';')
    return


def quality_check():
    global data

    if data.isnull().values.any():
        raise Exception("Data contains null values")
    return


with DAG(
    "pipeline",
) as dag:
    extract = PythonOperator(
        task_id="validate",
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
