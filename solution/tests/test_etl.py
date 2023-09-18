# import pytest
import types
from src.etl import _lazy_read_blocks, _process_approx_transaction_exec_time


def test_lazy_read_blocks():
    test_path = "solution/tests/test_txs.csv"
    block_dfs_gen = _lazy_read_blocks(test_path)
    assert isinstance(block_dfs_gen, types.GeneratorType)

    block_dfs = list(block_dfs_gen)
    # assert partition by block is OK
    assert len(block_dfs) == 2
    # assert that unique is effective
    assert block_dfs[0].to_series().len() == 2


def test_process_approx_transaction_exec_time():
    res = _process_approx_transaction_exec_time(
        block_timestamp="2023-08-01 07:04:59.000000 UTC", transactions_count=3
    )
    # if entire block length is 12 seconds
    # and there is only 3 transactions in the block
    # then each transaction takes approx 4 seconds - to decrement from the block ts.
    assert res == [
        "2023-08-01 07:04:55.000000 UTC",
        "2023-08-01 07:04:51.000000 UTC",
        "2023-08-01 07:04:47.000000 UTC",
    ]


# def test_cache_market_data():
#     test_path = "solution/tests/test_txs.csv"
#     txs = _lazy_read_blocks(test_path)

#     def fake_func(str):
#         print("stp")
#         fake_func.counter += 1
#         return 42.0

#     breakpoint()
#     fake_func.counter = 0
#     a = _process_data(txs, fake_func)
#     assert fake_func.counter == 2
