from airflow import DAG
from airflow.operators.bash import BashOperator
from pendulum import datetime

with DAG(
        dag_id='dbt_source_freshness_daily',
        start_date=datetime(2019, 1, 1),
        schedule_interval='@daily',
        tags=['validate'],
        catchup=False
) as dag:
    BashOperator(
        bash_command='source /opt/dbt-env/bin/activate && '
                     'dbt source snapshot-freshness --project-dir ${DBT_DIR}/finance-data',
        task_concurrency=1,
        task_id='dbt_source_freshness'
    )
