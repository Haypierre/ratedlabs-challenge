from fastapi.testclient import TestClient
import pytest

import re
from src.main import app


@pytest.fixture
def client() -> TestClient:
    client = TestClient(app)
    return client


def test_transactions_endpoint(client: TestClient):
    response = client.get(url="/transactions/NotATxHash")
    assert response.status_code == 404
    assert response.json() == {"detail": "NotATxHash NOT FOUND"}
    response = client.get(
        url="/transactions/0x5fde6d5674f9fc8538234ea7d873d226689af08269fdff6c62df4d00d40dc7e1"
    )
    assert response.status_code == 200
    result = response.json()
    # https://etherscan.io/tx/0x5fde6d5674f9fc8538234ea7d873d226689af08269fdff6c62df4d00d40dc7e1 # noqa: E501
    assert (
        result["hash"]
        == "0x5fde6d5674f9fc8538234ea7d873d226689af08269fdff6c62df4d00d40dc7e1"
    )
    assert result["fromAddress"] == "0x44c832526eabde3af5051e7dd36ef5410597a902"
    assert result["toAddress"] == "0xdef1c0ded9bec7f1a1670819833240f027b25eff"
    assert result["blockNumber"] == 17818533
    # "Aug-01-2023 07:03:04 AM +UTC"
    # Unfortunatelly, system can't predict exactly
    # the transcaation approximative execution time within a block
    # Because it doesn't read transactions in order.
    re.match("Aug-01-2023 07:0[0-9]{1}:[0-9]{2} AM +UTC", result["executedAt"])
    assert result["executedAt"].startswith("Aug-01-2023 07:0")
    assert result["gasUsed"] == 306341
    assert result["gasCostInDollars"] == 7.19


def test_stats_endpoint(client: TestClient):
    response = client.get(url="/stats")

    assert response.status_code == 200
    assert response.json() == {
        "totalTransactionsInDB": 5000,
        "totalGasUsed": 494112901,
        "totalGasCostInDollars": 19489,
    }
