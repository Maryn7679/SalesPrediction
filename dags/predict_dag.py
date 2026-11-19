import pandas as pd
import datetime as dt
from airflow.providers.standard.operators.python import PythonOperator
from airflow.sdk import DAG


def load_model(**context):
    return "No model yet :)"


def predict(**context):
    file = context["params"]["filename"]
    data = pd.read_csv(f"./data_files/{file}_grouped.csv", sep=';', header=0)
    start_time = dt.datetime.strptime(context["params"]["start_time"], '%Y.%m.%d %H:%M')
    end_time = dt.datetime.strptime(context["params"]["end_time"], '%Y.%m.%d %H:%M')

    date_range = pd.date_range(start=start_time, end=end_time, freq="D").date
    prediction = pd.DataFrame(data={"date": date_range,
                                    "order_count": [data["order_count"].mean()] * len(date_range),
                                    "orders_total": [data["orders_total"].mean()] * len(date_range)})
    prediction.to_csv(f"./data_files/predictions/{file}.csv", sep=';', index=False)

    return "Prediction complete"


with DAG(
    "predict",
    params = {
            "filename": "blinkit_orders_2",
            "start_time": "2023.03.16 00:00",
            "end_time": "2023.06.30 23:59",
        },
) as dag:
    load_model = PythonOperator(
        task_id="load_model",
        python_callable=load_model,
    )
    predict = PythonOperator(
        task_id="predict",
        python_callable=predict,
    )

    load_model >> predict


if __name__ == "__main__":
    dag.test()
