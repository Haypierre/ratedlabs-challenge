import polars as pl
import os
from datetime import datetime, timedelta
from typing import Iterator, Callable
from pathlib import Path
import requests
from db_utils import init, write_dataframe


def _process_approx_transaction_exec_time(
    block_timestamp: str, transactions_count: int, ethereum_average_block_time=12
) -> list[str]:
    approx_transaction_exec_time = ethereum_average_block_time / transactions_count

    upper_limit = datetime.strptime(block_timestamp, "%Y-%m-%d %H:%M:%S.%f %Z")
    txs = [
        (
            upper_limit - timedelta(seconds=delta * approx_transaction_exec_time)
        ).strftime(("%Y-%m-%d %H:%M:%S.%f") + " UTC")
        for delta in range(1, transactions_count + 1)
    ]
    assert len(txs) == transactions_count
    return txs


def _lazy_read_blocks() -> Iterator[pl.DataFrame]:
    root_dir = Path("../..")
    transactions = pl.scan_csv(
        source=root_dir / "coding-challenge" / "ethereum_txs.csv",
        dtypes={
            "hash": str,
            "nonce": pl.Float64,
            "block_hash": str,
            "block_number": pl.Float64,
            "transaction_index": pl.Float64,
            "from_address": str,
            "to_address": str,
            "value": pl.Float64,
            "gas": pl.Float64,
            "gas_price": pl.Float64,
            "block_timestamp": str,
            "max_fee_per_gas": pl.Float64,
            "max_priority_fee_per_gas": pl.Float64,
            "transaction_type": str,
            "receipts_cumulative_gas_used": pl.Float64,
            "receipts_gas_used": pl.Float64,
            "receipts_contract_address": str,
            "receipts_root": str,
            "receipts_status": str,
            "receipts_effective_gas_price": pl.Float64,
        },
        try_parse_dates=True,
    )
    transactions_by_block = transactions.unique().collect().partition_by("block_hash")
    for transactions in transactions_by_block:
        yield transactions


def _get_market_data(block_timestamp: str):
    coin_api_key = str(os.getenv("COIN_API_KEY"))
    time_end = datetime.strptime(block_timestamp, "%Y-%m-%d %H:%M:%S.%f UTC")
    time_start_str = (time_end - timedelta(seconds=12)).strftime("%Y-%m-%dT%H:%M:%S")
    time_end_str = time_end.strftime("%Y-%m-%dT%H:%M:%S")
    coin_url = f"https://rest.coinapi.io/v1/exchangerate/ETH/USD/history?period_id=5SEC&time_start={time_start_str}&time_end={time_end_str}"
    headers = {"X-CoinAPI-Key": coin_api_key}
    response = requests.get(coin_url, headers=headers)
    return response


def _process_data(
    blocks: Iterator[pl.DataFrame], extractor: Callable
) -> Iterator[pl.DataFrame]:
    for block in blocks:
        transactions_count = block.select(pl.count())[0, 0]
        block_timestamp = block.select("block_timestamp").unique()[0, 0]
        transaction_exec_times = pl.Series(
            name="approximative_execution_timestamp",
            values=_process_approx_transaction_exec_time(
                block_timestamp, transactions_count
            ),
            dtype=str,
        )
        block = block.with_columns(transaction_exec_times)
        block = block.with_columns(
            pl.col("gas").mul(pl.col("gas_price")).floordiv(1e9).alias("gas_cost")
        )
        extractor(block_timestamp)
        yield block


def _load(blocks: Iterator[pl.DataFrame]):
    for block in blocks:
        write_dataframe(block, table="transactions")


def launch_etl() -> None:
    init()
    # extract transactions from CSV in polars dataframes
    blocks = _lazy_read_blocks()
    # apply require transformations
    # * add approximative transcation execution time
    # * add gas_cost
    # * retrieve from external source the approximate
    # price of ETH at transaction execution time
    enriched_transactions = _process_data(blocks, _get_market_data)
    # Populate a local database with the processed transactions.
    _load(enriched_transactions)
