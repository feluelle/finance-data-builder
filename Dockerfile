FROM apache/airflow:2.0.0b3-python3.8

USER root

# Additional requirements for Airflow
COPY requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt

# DBT Installation from https://docs.getdbt.com/dbt-cli/installation/#installation
## Requirements for DBT
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
           git \
           nano \
    && apt-get autoremove -yqq --purge \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*
## DBT installed in a Python Virtual Environment
RUN python3 -m venv /opt/dbt-env \
    && source /opt/dbt-env/bin/activate \
    && pip install dbt

USER airflow
