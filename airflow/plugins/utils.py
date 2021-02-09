from os import getenv

from sqlalchemy import create_engine, VARCHAR
from sqlalchemy.engine.url import URL


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


def load_df_into_db(data_frame, schema: str, table: str) -> None:
    engine = create_engine(URL(
        username=getenv('DBT_POSTGRES_USER'),
        password=getenv('DBT_POSTGRES_PASSWORD'),
        host=getenv('DBT_POSTGRES_HOST'),
        port=getenv('DBT_POSTGRES_PORT'),
        database=getenv('DBT_POSTGRES_DB'),
        drivername='postgres'
    ))
    with engine.connect() as cursor:
        cursor.execute(f'CREATE SCHEMA IF NOT EXISTS {schema}')
    data_frame.to_sql(
        schema=schema,
        name=table,
        dtype=VARCHAR,
        if_exists='append',
        con=engine,
        method=_psql_insert_copy,
        index=False
    )
