import os
import pandas as pd
import datetime as dt
from airflow.providers.standard.operators.python import PythonOperator
from airflow.sdk import DAG


def extract(**context):
    file = context["params"]["filename"]
    data = pd.read_csv(f"./data_files/{file}.csv", sep=';', header=0)
    data.to_csv(f"./data_files/temp/{file}.csv", sep=';', index=False)

    return "Data pulled"


def validate(**context):
    file = context["params"]["filename"]
    start = context["params"]["start_time"]
    end = context["params"]["end_time"]

    start_time = dt.datetime.strptime(start, '%Y.%m.%d %H:%M')
    end_time = dt.datetime.strptime(end, '%Y.%m.%d %H:%M')

    data = pd.read_csv(f"./data_files/temp/{file}.csv", sep=';', header=0)

    if not {'order_id', 'customer_id', 'order_date', 'promised_delivery_time',
            'actual_delivery_time', 'delivery_status', 'order_total', 'payment_method',
            'delivery_partner_id', 'store_id'}.issubset(data.columns):
        raise Exception(f"Data is missing required columns. Data example: {data.iloc[1]}")
    if start_time >= end_time:
        raise Exception("Incorrect input parameters")
    return "Data format validated"


def quality_check(**context):
    file = context["params"]["filename"]
    data = pd.read_csv(f"./data_files/temp/{file}.csv", sep=';', header=0)

    if data.isnull().values.any():
        raise Exception("Data contains null values")

    return "Data quality checked"


def transform(**context):
    file = context["params"]["filename"]
    data = pd.read_csv(f"./data_files/temp/{file}.csv", sep=';', header=0)

    start = context["params"]["start_time"]
    end = context["params"]["end_time"]

    start_time = dt.datetime.strptime(start, '%Y.%m.%d %H:%M')
    end_time = dt.datetime.strptime(end, '%Y.%m.%d %H:%M')

    data = data[["order_id", "customer_id", "order_date", "order_total"]]
    data["order_date"] = pd.to_datetime(data["order_date"], format="%d.%m.%Y %H:%M")
    data = data[(data['order_date'] > start_time) and (data['order_date'] < end_time)]

    data.to_csv(f"./data_files/temp/{file}.csv", sep=';', index=False)

    return "Data transformed"


def load(**context):
    file = context["params"]["filename"]
    data = pd.read_csv(f"./data_files/temp/{file}.csv", sep=';', header=0)
    return_string = "Data loaded"

    data["order_date"] = data["order_date"].astype("datetime64[ns]")
    totals = data.groupby([data["order_date"].dt.date])['order_total'].sum()
    counts = data.groupby([data["order_date"].dt.date])['order_total'].count()
    data2 = pd.DataFrame(data={"date": data["order_date"],
                               "order_count": counts,
                               "orders_total": totals})
    data2.to_csv(f"./data_files/features/{file}_grouped.csv", sep=';', index=False)

    data.to_csv(f"./data_files/features/{file}.csv", sep=';', index=False)

    return return_string


with DAG(
    "data_load",
    params = {
            "filename": "blinkit_orders_2",
            "start_time": "2023.03.16 00:00",
            "end_time": "2023.06.30 23:59",
        },
) as dag:
    extract = PythonOperator(
        task_id="extract",
        python_callable=extract,
    )
    validate = PythonOperator(
        task_id="validate",
        python_callable=validate,
    )
    transform = PythonOperator(
        task_id="transform",
        python_callable=transform,
    )
    load = PythonOperator(
        task_id="load",
        python_callable=load,
    )
    quality_check = PythonOperator(
        task_id="quality_check",
        python_callable=quality_check,
    )

    extract >> [validate, quality_check] >> transform >> load

if __name__ == "__main__":
    dag.test()
