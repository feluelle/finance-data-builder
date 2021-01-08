import json

import pandas as pd
from airflow import DAG
from airflow.operators.bash import BashOperator
from airflow.operators.latest_only import LatestOnlyOperator
from airflow.operators.python import PythonOperator
from airflow.providers.http.operators.http import SimpleHttpOperator
from pendulum import datetime

from plugins.utils import load_df_into_db

with DAG(dag_id='paypal_daily', start_date=datetime(2019, 1, 1), schedule_interval='@daily') as dag:
    task_extract_transactions = SimpleHttpOperator(
        endpoint='/v1/reporting/transactions',
        method='GET',
        data={
            'start_date': '{{ execution_date.isoformat() }}',
            'end_date': '{{ next_execution_date.isoformat() }}'
        },
        headers={
            'Content-Type': 'application/json'
        },
        http_conn_id='http_paypal',
        task_id='extract_transactions'
    )


    def load_transactions(data: str) -> None:
        # Read data from xcom
        data_dict = json.loads(data)
        # Remove api meta data (only needed for paging)
        del data_dict['page']
        del data_dict['total_items']
        del data_dict['total_pages']
        del data_dict['links']
        # Load data into dataframe
        data_frame = pd.DataFrame(data=data_dict)
        # Load data into db
        load_df_into_db(data_frame, schema='paypal', table='src_paypal_transactions')


    task_load_transactions = PythonOperator(
        python_callable=load_transactions,
        op_kwargs=dict(data=task_extract_transactions.output),
        task_id='load_transactions'
    )

    task_latest_only = LatestOnlyOperator(
        trigger_rule='all_done',
        task_id='latest_only'
    )
    task_transform = BashOperator(
        bash_command='source /opt/dbt-env/bin/activate && '
                     'dbt run --project-dir /opt/dbt/finance-data --models staging.paypal+',
        task_concurrency=1,
        task_id='transform_paypal_data'
    )
    task_test = BashOperator(
        bash_command='source /opt/dbt-env/bin/activate && '
                     'dbt test --project-dir /opt/dbt/finance-data --models staging.paypal+',
        task_concurrency=1,
        task_id='test_paypal_data'
    )

    task_extract_transactions >> task_load_transactions >> task_latest_only >> task_transform >> task_test
