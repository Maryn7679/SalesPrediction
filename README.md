# SalesPrediction
Maryna Kosse

An ML system which predicts the sales revenue of various grocery products based on 
previous sales for the next week. 
New sales data is added daily and the model is continuously evaluated on its performance and
improved over time.

Run:

`docker-compose up -d`
```commandline
docker exec -it airflow /bin/bash
airflow db migrate
airflow dag-processor
airflow scheduler
```
```commandline
docker exec -it minio /bin/bash
mc alias set local http://localhost:9000 admin password123
mc cp local/order-data/blinkit_orders_2.csv data/files
```
db migrate must be run immediately after opening shell
before the container shuts down.

| Property                                   | Evidence a reviewer checks                                                             | Added in |
|--------------------------------------------|----------------------------------------------------------------------------------------|----------|
| Repository reproducible from a clean clone | CI is green; make setup and make lint succeed on a fresh clone                         | Lab 1    |
| Design document exists and is current      | `docs/design.md` follows the template, every section filled or marked as an assumption | Lab 1    |
