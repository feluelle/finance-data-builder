FROM apache/airflow:2.0.1-python3.8

# Additional requirements for Airflow
COPY requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt
COPY ./airflow/dags ${AIRFLOW_HOME}/dags
COPY ./airflow/plugins ${AIRFLOW_HOME}/plugins

USER root

# DBT Installation from https://docs.getdbt.com/dbt-cli/installation/#installation
## Requirements for DBT
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
           git \
           nano \
    && apt-get autoremove -yqq --purge \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*
## Create virtual environment for DBT
RUN python3 -m venv /opt/dbt-env \
    && chown airflow -R /opt/dbt-env

USER airflow

## DBT installed in a Python Virtual Environment
ENV DBT_DIR /opt/dbt
ENV DBT_PROFILES_DIR ${DBT_DIR}
COPY --chown=airflow ./dbt ${DBT_DIR}
RUN source /opt/dbt-env/bin/activate \
    && pip install dbt \
    && dbt deps --project-dir ${DBT_DIR}/finance-data
# Expose additional port for dbt docs serve
EXPOSE 8081
