import os
import pandas as pd
import datetime as dt
from airflow.providers.standard.operators.bash import BashOperator
from airflow.providers.standard.operators.python import PythonOperator
from airflow.sdk import DAG, task


data = pd.DataFrame()


def extract():
    os.system('dvc pull')

    global data
    data = pd.read_csv("Data/blinkit_orders.csv", sep=';')

    return "dvc data pulled"


def validate(params):
    global data

    if not {'order_id', 'customer_id', 'order_date', 'promised_delivery_time',
            'actual_delivery_time', 'delivery_status', 'order_total', 'payment_method',
            'delivery_partner_id', 'store_id'}.issubset(data.columns):
        raise Exception("Data is missing required columns")
    if params.start_time > params.end_time:
        raise Exception("Incorrect input parameters")
    return "Data format validated"


def quality_check():
    global data

    if data.isnull().values.any():
        raise Exception("Data contains null values")

    return "Data quality checked"


def transform(params):
    global data

    data = data[["order_id", "customer_id", "order_date", "order_total"]]
    data["order_date"] = pd.to_datetime(data["order_date"], format="%d.%m.%Y %H:%M")
    data = data[(data['order_date'] > params.start_time) & (data['order_date'] < params.end_time)]

    return "Data transformed"


def load():
    global data

    old_data = pd.read_csv("Data/Features/blinkit_orders_features.csv", sep=';')
    data = pd.merge(old_data, data, "outer", on="order_id")

    data.to_csv("Data/Features/blinkit_orders_features.csv", sep=';')

    return "Data loaded"


with DAG(
    "pipeline",
    params = {
        "start_time": dt.datetime(2023, 3, 16, 0, 0),
        "end_time": dt.datetime(2023, 6, 30, 23, 59),
        },
) as dag:
    extract = PythonOperator(
        task_id="validate",
        python_callable=extract
    ),
    validate = PythonOperator(
        task_id="validate",
        python_callable=validate,
        params={"start_time", "end_time"}
    ),
    transform = PythonOperator(
        task_id="transform",
        python_callable=transform,
        params={"start_time", "end_time"}
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


if __name__ == "__main__":
    dag.test(
     run_conf={
        "start_time": dt.datetime(2023, 3, 16, 0, 0),
        "end_time": dt.datetime(2023, 6, 30, 23, 59),
        },
    )
