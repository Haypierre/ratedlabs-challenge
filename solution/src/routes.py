from fastapi import APIRouter

from models import Transaction

from transactions import transaction_service

router = APIRouter()


@router.get("/transactions/{hash}", status_code=200)
def get_transaction(hash: str) -> Transaction:
    return transaction_service.get_transactions(hash)
