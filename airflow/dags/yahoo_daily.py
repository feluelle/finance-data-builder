from os import getenv
from pathlib import Path

import pandas as pd
import yfinance as yf
from airflow import DAG
from airflow.exceptions import AirflowSkipException
from airflow.operators.bash import BashOperator
from airflow.operators.latest_only import LatestOnlyOperator
from airflow.operators.python import PythonOperator
from pendulum import datetime

from plugins.utils import load_df_into_db

LOCAL_STORAGE = getenv('LOCAL_STORAGE', '/tmp')

with DAG(dag_id='yahoo_daily', start_date=datetime(2019, 1, 1), schedule_interval='0 0 * * 1-5') as dag:
    def extract_finance_data(ticker: str, ds: str, next_ds: str, **kwargs: dict) -> str:
        directory, file = f'{LOCAL_STORAGE}/yahoo/{ticker}', f'{ds}.csv'
        # Create directory in case it does not already exist
        path = Path(directory)
        path.mkdir(parents=True, exist_ok=True)
        # Download data
        data_frame = yf.download(
            tickers=ticker,
            start=ds,
            end=next_ds,
            interval='60m',
            actions=True,
            progress=False
        )
        if data_frame.empty:
            raise AirflowSkipException('No data available!')
        # Write data to storage in csv format
        full_path = path.joinpath(file)
        data_frame.to_csv(path_or_buf=full_path)
        return str(full_path)


    def load_finance_data(ticker: str, file: str) -> None:
        # Read data from storage
        data_frame = pd.read_csv(file)
        # Add meta data
        data_frame['Ticker'] = ticker
        # Load data into db
        load_df_into_db(data_frame, schema='yahoo', table='src_yahoo_finance')


    task_latest_only = LatestOnlyOperator(
        trigger_rule='all_done',
        task_id='latest_only'
    )
    task_transform = BashOperator(
        bash_command='source /opt/dbt-env/bin/activate && '
                     'dbt run --project-dir /opt/dbt/finance-data --models staging.yahoo+',
        task_concurrency=1,
        task_id='transform_finance_data'
    )
    task_test = BashOperator(
        bash_command='source /opt/dbt-env/bin/activate && '
                     'dbt test --project-dir /opt/dbt/finance-data --models staging.yahoo+',
        task_concurrency=1,
        task_id='test_finance_data'
    )
    for ticker in ['msft', 'aapl', 'goog', 'amzn', 'fb', 'baba', 'tsla', 'wmt', 'nvda', 'unh']:
        task_extract = PythonOperator(
            python_callable=extract_finance_data,
            op_args=[ticker],
            task_id=f'extract_finance_data_{ticker}'
        )
        task_load = PythonOperator(
            python_callable=load_finance_data,
            op_args=[ticker],
            op_kwargs=dict(file=task_extract.output),
            task_id=f'load_finance_data_{ticker}'
        )
        task_extract >> task_load >> task_latest_only >> task_transform >> task_test
