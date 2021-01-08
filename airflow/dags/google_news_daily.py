from os import getenv
from pathlib import Path

import pandas as pd
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.latest_only import LatestOnlyOperator
from airflow.operators.python import PythonOperator
from pendulum import datetime
from pygooglenews import GoogleNews

from plugins.utils import load_df_into_db

LOCAL_STORAGE = getenv('LOCAL_STORAGE', '/tmp')

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
        load_df_into_db(data_frame, schema='google', table='src_google_news')


    task_latest_only = LatestOnlyOperator(
        trigger_rule='all_done',
        task_id='latest_only'
    )
    task_transform = BashOperator(
        bash_command='source /opt/dbt-env/bin/activate && '
                     'dbt run --project-dir /opt/dbt/finance-data --models staging.google+',
        task_concurrency=1,
        task_id='transform_google_news_data'
    )
    task_test = BashOperator(
        bash_command='source /opt/dbt-env/bin/activate && '
                     'dbt test --project-dir /opt/dbt/finance-data --models staging.google+',
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
