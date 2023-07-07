import datetime
from dataclasses import dataclass

from src.application.transaction.repository import TransactionRepository, TransactionAlreadyExists
from src.domain.transaction import AccountId, Transaction
from src.domain.transaction import TransactionId
from src.shared.application.repository import EntityAlreadyExists


@dataclass(frozen=True)
class TransactionCreationRequest:
    id: TransactionId
    account_id: AccountId
    date: datetime.date
    label: str
    amount: float


class TransactionCreator:
    def __init__(self, repository: TransactionRepository) -> None:
        self._repository = repository

    def create(self, request: TransactionCreationRequest) -> None:
        transaction = Transaction(
            id_=request.id, account_id=request.account_id, date=request.date, label=request.label, amount=request.amount
        )

        try:
            self._repository.add(transaction)
        except EntityAlreadyExists as e:
            raise TransactionAlreadyExists(transaction_id=request.id) from e
