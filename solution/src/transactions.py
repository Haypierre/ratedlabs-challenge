from models import Stats, Transaction
from fastapi import HTTPException

from db_utils import execute_query


class TransactionService:
    def get_transactions(self, tx_hash: str):
        try:
            txs = execute_query(f"select * from transactions where hash = '{tx_hash}'")
            unique_tx = txs[0]
        except IndexError:
            raise HTTPException(status_code=404, detail=f"{tx_hash} NOT FOUND")

        return Transaction(
            hash=unique_tx["hash"],
            fromAddress=unique_tx["from_address"],
            toAddress=unique_tx["to_address"],
            blockNumber=unique_tx["block_number"],
            executedAt=unique_tx["approximative_execution_timestamp"],
            gasUsed=unique_tx["gas"],
            gasCostInDollars=42,
        )

    def get_stats(self):
        try:
            total_transactions_in_db = execute_query(
                "select count(*) from transactions"
            ).pop()
            total_gas_used = execute_query("select sum(gas) from transactions").pop()
            # total_gas_cost_in_dollars =
            # execute_query("select sum(gas_cost) from transactions")

            return Stats(
                totalTransactionsInDB=total_transactions_in_db["count"],
                totalGasUsed=total_gas_used["sum"],
                totalGasCostInDollars=42,
            )

        except Exception:
            pass


transaction_service = TransactionService()
