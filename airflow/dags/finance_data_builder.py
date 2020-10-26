from os import getenv

import pandas as pd
import yfinance as yf
from airflow import DAG
from airflow.exceptions import AirflowSkipException
from airflow.operators.bash import BashOperator
from airflow.operators.python import PythonOperator
from pendulum import datetime
from sqlalchemy import create_engine

LOCAL_STORAGE = getenv('LOCAL_STORAGE', '/tmp')
DBT_DB_SQL_ALCHEMY_CONN = getenv('DBT_DB_SQL_ALCHEMY_CONN')


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


with DAG(dag_id='finance_data_builder', start_date=datetime(2020, 1, 1)) as dag:
    def extract_finance_data(ticker, ds, next_ds, **kwargs):
        file = f'{LOCAL_STORAGE}/{ticker}_{ds}_{next_ds}.csv'
        data_frame = yf.download(ticker, start=ds, end=next_ds, interval='1h')
        if data_frame.empty:
            raise AirflowSkipException('No data available!')
        data_frame.to_csv(path_or_buf=file)
        return file


    def load_finance_data(ticker, file):
        data_frame = pd.read_csv(file)
        data_frame.to_sql(
            name=f'"src_{ticker}"',
            if_exists='append',
            con=create_engine(DBT_DB_SQL_ALCHEMY_CONN),
            method=_psql_insert_copy,
            index=False
        )


    tasks_load = []
    for ticker in ['MSFT']:
        task_extract = PythonOperator(
            python_callable=extract_finance_data,
            op_args=[ticker],
            task_id='extract_finance_data'
        )
        task_load = PythonOperator(
            python_callable=load_finance_data,
            op_args=[ticker],
            op_kwargs=dict(file=task_extract.output),
            task_id='load_finance_data'
        )
        task_extract >> task_load
        tasks_load.append(task_load)
    task_transform = BashOperator(
        bash_command='source /dbt-env/bin/activate && dbt run',
        task_id='transform_finance_data'
    )
    tasks_load >> task_transform
