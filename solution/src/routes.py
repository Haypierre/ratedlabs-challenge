from fastapi import APIRouter

from models import Stats, Transaction

from transactions import transaction_service

router = APIRouter()


@router.get("/transactions/{hash}", status_code=200)
def get_transaction(hash: str) -> Transaction:
    return transaction_service.get_transactions(hash)


@router.get("/stats", status_code=200)
def get_stats() -> Stats:
    return transaction_service.get_stats()
