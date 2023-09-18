import polars as pl
from datetime import datetime, timedelta
from typing import Iterator, Callable, Optional
from pathlib import Path
import requests
from src.db_utils import init, write_dataframe
from functools import cache


def _process_approx_transaction_exec_time(
    block_timestamp: str, transactions_count: int, ethereum_average_block_time=12
) -> list[str]:
    """
    Helper function to calulate approximative transactions execution time.
    Will be given as a UDF to polars.
    """

    # TODO: find a native solution with polars API to achieve the same work
    # without needing a UDF. UDF can't be optimized and are running way slower.

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


def _lazy_read_blocks(path: str) -> Iterator[pl.DataFrame]:
    """
    Lazy load of the "ethereum_txs.csv" into polars dataframes
    """
    root_dir = Path("..")
    transactions = pl.scan_csv(
        source=root_dir.joinpath(path),
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


@cache
def _get_market_data(block_day_date: str) -> float:
    """
    Retrieve ethereum price for the transaction day from CoinGecko API.
    Cache the result to avoid getting rate limited with a larger dataset.
    """
    response = requests.get(
        url=f"https://api.coingecko.com/api/v3/coins/ethereum/history?date={block_day_date}"
    )
    eth_price_in_usd = response.json()["market_data"]["current_price"]["usd"]
    return float(eth_price_in_usd)


def _process_data(
    blocks: Iterator[pl.DataFrame], extractor: Optional[Callable] = lambda _: 0
) -> Iterator[pl.DataFrame]:
    """
    Transform `blocks`.
    Apply the following transformations:
         - calculate approximatve execution time for all transActions (pure operation)
         - calculate the gas cost in Gwei for all transactions (pure operation)
         - get market data to calculate the gas cost in dollars (API call: side effects)

    :param blocks: the blocks of transactions
    :type blocks: Iterator[pl.DataFrame]
    :param extractor: Optional function to extract market data from an external source
    :type extractor: Optional[Callable]
    :return: the enriched blocks:
    :rtype: Iterator[pl.DataFrame]
    """
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
        # Gas Cost = Gas Price * Gas used by transaction
        block = block.with_columns(
            pl.col("receipts_gas_used")
            .mul(pl.col("receipts_effective_gas_price"))
            .truediv(1e9)  # Wei to Gwei
            .alias("gas_cost")
        )
        if extractor:
            block_date = datetime.strptime(block_timestamp, "%Y-%m-%d %H:%M:%S.%f UTC")
            block_day_date = block_date.strftime("%d-%m-%Y")
            current_eth_price = extractor(block_day_date)
            block = block.with_columns(
                pl.col("gas_cost")
                .truediv(1e9)  # Gwei to ETH
                .mul(current_eth_price)
                .alias("gas_cost_in_dollars")
            )
        yield block


def _load(blocks: Iterator[pl.DataFrame]):
    for block in blocks:
        write_dataframe(block, table="transactions")


def launch_etl() -> None:
    init()
    # extract transactions from CSV into polars dataframes
    blocks = _lazy_read_blocks("coding-challenge/ethereum_txs.csv")
    # apply required transformations
    # * add approximative transactions execution time
    # * add gas_cost
    # * retrieve from external source the approximate
    # price of ETH at transaction execution time
    enriched_transactions = _process_data(blocks, _get_market_data)
    # Populate a local database with the processed transactions.
    _load(enriched_transactions)
