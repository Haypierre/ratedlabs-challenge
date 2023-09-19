# mypy: ignore-errors

import types
from src.etl import (
    _lazy_read_blocks,
    _process_approx_transaction_exec_time,
    _process_data,
)


def test_lazy_read_blocks():
    test_path = "solution/tests/test_txs.csv"
    block_dfs_gen = _lazy_read_blocks(test_path)
    assert isinstance(block_dfs_gen, types.GeneratorType)

    block_dfs = list(block_dfs_gen)
    # assert partition by block is OK
    assert len(block_dfs) == 1
    # assert that unique is effective
    assert block_dfs[0].to_series().len() == 2


def test_process_approx_transaction_exec_time():
    res = _process_approx_transaction_exec_time(
        block_timestamp="2023-08-01 07:04:59.000000 UTC", transactions_count=3
    )
    # if entire block length is 12 seconds
    # and there is only 3 transactions in the block
    # then each transaction takes approx 4 seconds - to decrement from the block ts.

    res.sort()
    assert res == [
        "Aug-01-2023 07:04:47 AM +UTC",
        "Aug-01-2023 07:04:51 AM +UTC",
        "Aug-01-2023 07:04:55 AM +UTC",
    ]


def test_cache_market_data():
    test_path = "solution/tests/test_txs.csv"
    blocks = _lazy_read_blocks(test_path)

    def fake_eth_market_price(block_ts: str):
        fake_eth_market_price.counter += 1
        return 1845

    fake_eth_market_price.counter = 0
    processed_blocks = _process_data(blocks, fake_eth_market_price)
    print(list(processed_blocks))
    # only 1 date in the test data
    assert fake_eth_market_price.counter == 1


def test_gas_cost_calculation():
    test_path = "solution/tests/test_txs.csv"
    blocks = _lazy_read_blocks(test_path)

    def fake_eth_market_price(block_ts: str):
        return 1845

    fist_processed_block = next(_process_data(blocks, fake_eth_market_price))

    fist_processed_block.to_dict()["hash"].to_list() == [
        "0x6f218a5e009c56f8db17e933af7cc98360b699ae88cb85ef31c3eb351ecdee24",
        "0xc055b65e39c15e1bc90cb4ccb2daac6b59c02ec1aa6c4216276054b4f31ed90a",
    ]
    approx_paid_fees_in_dollars = [
        int(x) for x in fist_processed_block.to_dict()["gas_cost_in_dollars"].to_list()
    ]

    # https://etherscan.io/tx/0xc055b65e39c15e1bc90cb4ccb2daac6b59c02ec1aa6c4216276054b4f31ed90a
    # https://etherscan.io/tx/0x6f218a5e009c56f8db17e933af7cc98360b699ae88cb85ef31c3eb351ecdee24

    approx_paid_fees_in_dollars.sort()

    assert approx_paid_fees_in_dollars == [7, 12]
