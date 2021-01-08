# finance-data-builder

> Finance 🏦 Data Builder 🛠️ @ postgres 🐘

The finance data builder **extracts** data from several sources, **loads** it into a postgres database and 
**transforms** it via dbt into beautiful models.

The data sources are:
* [yahoo! finance](https://finance.yahoo.com/)
* [Google News](https://news.google.com/)
* [PayPal](https://www.paypal.com/)
    * [transactions](https://developer.paypal.com/docs/api/transaction-search/v1/)

## What it is

### Airflow

I use [Airflow](http://airflow.apache.org/) to **manage** the whole **ELT** process:

For **Google News**:

![airflow graph google news](images/airflow_graph__google_news.png "Airflow Graph - Google News")

For **yahoo! finance**:

![airflow graph yahoo](images/airflow_graph__yahoo.png "Airflow Graph - Yahoo")

For **PayPal**:

![airflow graph paypal](images/airflow_graph__paypal.png "Airflow Graph - PayPal")

### DBT

I use [DBT](https://www.getdbt.com/) to **transform** the data into **models**:

![dbt graph](images/dbt_graph.png "DBT Graph")

## Get started

### Prerequisites

- [docker](https://www.docker.com/)
- [docker-compose](https://docs.docker.com/compose/)

### Setup

To run this project, simply add a `.env` file to the project root directory, fill it with the following environment 
variables:
```bash
DBT_POSTGRES_HOST=fdb_dbt_db
DBT_POSTGRES_USER=dbt
DBT_POSTGRES_PASSWORD=dbt
DBT_POSTGRES_DB=dbt
DBT_POSTGRES_PORT=5432

AIRFLOW_POSTGRES_HOST=fdb_airflow_db
AIRFLOW_POSTGRES_USER=airflow
AIRFLOW_POSTGRES_PASSWORD=airflow
AIRFLOW_POSTGRES_DB=airflow
AIRFLOW_POSTGRES_PORT=5432

AIRFLOW_USER=airflow
AIRFLOW_PASSWORD=airflow
```
and then run it via `docker-compose`:
```bash
docker-compose up -d
```

### Notes

I am using a `storage` folder for storing data files locally. Normally you probably want the storage to be a remote 
storage that is designed to store large amount of data, such as S3, GCP or Blob Storage.