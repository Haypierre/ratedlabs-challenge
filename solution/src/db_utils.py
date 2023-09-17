import psycopg2
from psycopg2 import extras
import os
import polars as pl

db_params = {
    "dbname": os.getenv("DB_NAME"),
    "user": os.getenv("DB_USER"),
    "password": os.getenv("DB_PASSWORD"),
    "host": os.getenv("DB_HOST"),
    "port": os.getenv("DB_PORT"),
}


def execute_query(sql: str):
    connection = psycopg2.connect(**db_params)
    try:
        cursor = connection.cursor(cursor_factory=extras.RealDictCursor)
        cursor.execute(sql)
        connection.commit()
        if sql.lower().startswith("select"):
            return cursor.fetchall()
    except (Exception, psycopg2.Error) as error:
        print(f"Error while running sql statement {sql}", error)
    finally:
        if connection:
            cursor.close()
            connection.close


def init():
    """
    Launched once when starting the ETL.
    Make the ETL idempotent.
    Delete tabled if exists to start from green field.
    Creatae transactions table with UNIQUE constraint on tx_hash.
    """
    delete_table = "DROP TABLE IF EXISTS transactions"
    create_table_query = """
        CREATE TABLE IF NOT EXISTS transactions (
            id SERIAL PRIMARY KEY,
            hash VARCHAR(255) UNIQUE NOT NULL,
            nonce DOUBLE PRECISION,
            block_hash VARCHAR(255),
            block_number DOUBLE PRECISION,
            transaction_index DOUBLE PRECISION,
            from_address VARCHAR(255),
            to_address VARCHAR(255),
            value DOUBLE PRECISION,
            gas DOUBLE PRECISION,
            gas_price DOUBLE PRECISION,
            gas_cost DOUBLE PRECISION,
            block_timestamp VARCHAR(255),
            max_fee_per_gas DOUBLE PRECISION,
            max_priority_fee_per_gas DOUBLE PRECISION,
            transaction_type VARCHAR(255),
            receipts_cumulative_gas_used DOUBLE PRECISION,
            receipts_gas_used DOUBLE PRECISION,
            receipts_contract_address VARCHAR(255),
            receipts_root VARCHAR(255),
            receipts_status VARCHAR(255),
            receipts_effective_gas_price DOUBLE PRECISION,
            approximative_execution_timestamp VARCHAR(255)
        )
    """
    execute_query(delete_table)
    execute_query(create_table_query)


def write_dataframe(df: pl.DataFrame, table: str):
    df.write_database(
        table_name=table,
        if_exists="append",
        connection=f"postgresql://{db_params['user']}:{db_params['password']}@{db_params['host']}:{db_params['port']}/{db_params['dbname']}",
    )
