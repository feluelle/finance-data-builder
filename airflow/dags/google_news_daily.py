from os import getenv
from pathlib import Path

import pandas as pd
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.latest_only import LatestOnlyOperator
from airflow.operators.python import PythonOperator
from pendulum import datetime
from pygooglenews import GoogleNews
from sqlalchemy import create_engine, VARCHAR
from sqlalchemy.engine.url import URL

LOCAL_STORAGE = getenv('LOCAL_STORAGE', '/tmp')
DBT_POSTGRES_USER = getenv('DBT_POSTGRES_USER')
DBT_POSTGRES_PASSWORD = getenv('DBT_POSTGRES_PASSWORD')
DBT_POSTGRES_DB = getenv('DBT_POSTGRES_DB')
DBT_POSTGRES_HOST = getenv('DBT_POSTGRES_HOST')
DBT_POSTGRES_PORT = getenv('DBT_POSTGRES_PORT')


def _psql_insert_copy(table, conn, keys, data_iter):
    """
    Execute SQL statement inserting data

    Parameters
    ----------
    table : pandas.io.sql.SQLTable
    conn : sqlalchemy.engine.Engine or sqlalchemy.engine.Connection
    keys : list of str
        Column names
    data_iter : Iterable that iterates the values to be inserted
    """
    # Alternative to_sql() *method* for DBs that support COPY FROM
    import csv
    from io import StringIO

    # gets a DBAPI connection that can provide a cursor
    dbapi_conn = conn.connection
    with dbapi_conn.cursor() as cur:
        s_buf = StringIO()
        writer = csv.writer(s_buf)
        writer.writerows(data_iter)
        s_buf.seek(0)

        columns = ', '.join('"{}"'.format(k) for k in keys)
        if table.schema:
            table_name = '{}.{}'.format(table.schema, table.name)
        else:
            table_name = table.name

        sql = 'COPY {} ({}) FROM STDIN WITH CSV'.format(
            table_name, columns)
        cur.copy_expert(sql=sql, file=s_buf)


with DAG(dag_id='google_news_daily', start_date=datetime(2019, 1, 1), schedule_interval='@daily') as dag:
    def extract_news_data(company: str, ds: str, next_ds: str, **kwargs: dict) -> str:
        directory, file = f'{LOCAL_STORAGE}/google_news/{company}', f'{ds}.csv'
        # Create directory in case it does not already exist
        path = Path(directory)
        path.mkdir(parents=True, exist_ok=True)
        # Download data
        google_news_data = GoogleNews().search(query=company, from_=ds, to_=next_ds)
        # TODO: Maybe store the "feed", too.
        data_frame = pd.DataFrame(data=google_news_data['entries'])
        # Write data to storage in csv format
        full_path = path.joinpath(file)
        data_frame.to_csv(path_or_buf=full_path)
        return str(full_path)


    def load_news_data(company: str, file: str) -> None:
        # Read data from storage
        data_frame = pd.read_csv(file)
        # Add meta data
        data_frame['Company'] = company
        # Load data into db
        engine = create_engine(URL(
            username=DBT_POSTGRES_USER,
            password=DBT_POSTGRES_PASSWORD,
            host=DBT_POSTGRES_HOST,
            port=DBT_POSTGRES_PORT,
            database=DBT_POSTGRES_DB,
            drivername='postgres'
        ))
        schema = 'google_news'
        with engine.connect() as cursor:
            cursor.execute(f'CREATE SCHEMA IF NOT EXISTS {schema}')
        data_frame.to_sql(
            name='src_google_news',
            schema=schema,
            dtype=VARCHAR,
            if_exists='append',
            con=create_engine(URL(
                username=DBT_POSTGRES_USER,
                password=DBT_POSTGRES_PASSWORD,
                host=DBT_POSTGRES_HOST,
                port=DBT_POSTGRES_PORT,
                database=DBT_POSTGRES_DB,
                drivername='postgres'
            )),
            method=_psql_insert_copy,
            index=False
        )


    task_latest_only = LatestOnlyOperator(
        trigger_rule='all_done',
        task_id='latest_only'
    )
    task_transform = BashOperator(
        bash_command='source /opt/dbt-env/bin/activate && '
                     'dbt run --project-dir /opt/dbt/finance-data --models stg_google_news+',
        task_concurrency=1,
        task_id='transform_google_news_data'
    )
    task_test = BashOperator(
        bash_command='source /opt/dbt-env/bin/activate && '
                     'dbt test --project-dir /opt/dbt/finance-data --models stg_google_news+',
        task_concurrency=1,
        task_id='test_google_news_data'
    )
    for company in [
        'microsoft',
        'apple',
        'google',
        'amazon',
        'facebook',
        'alibaba',
        'tesla',
        'walmart',
        'nvidia',
        'unitedhealth'
    ]:
        task_extract = PythonOperator(
            python_callable=extract_news_data,
            op_args=[company],
            task_id=f'extract_google_news_data_{company}'
        )
        task_load = PythonOperator(
            python_callable=load_news_data,
            op_args=[company],
            op_kwargs=dict(file=task_extract.output),
            task_id=f'load_google_news_data_{company}'
        )
        task_extract >> task_load >> task_latest_only >> task_transform >> task_test
