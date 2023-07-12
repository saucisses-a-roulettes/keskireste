from dataclasses import dataclass
import datetime

from src.application.transaction.repository import TransactionRepository, TransactionNotFound
from src.domain.account import AccountId
from src.domain.transaction import TransactionId
from src.shared.application.repository import EntityNotFound


@dataclass(frozen=True)
class TransactionUpdateRequest:
    id: TransactionId
    date: datetime.date
    label: str
    amount: float


class TransactionUpdater:
    def __init__(self, repository: TransactionRepository) -> None:
        self._repository = repository

    def update(self, request: TransactionUpdateRequest) -> None:
        try:
            transaction = self._repository.retrieve(request.id)
        except EntityNotFound as e:
            raise TransactionNotFound(transaction_id=request.id) from e

        transaction.rectify_amount(request.amount)
        transaction.rectify_date(request.date)
        transaction.modify_label(request.label)

        self._repository.update(transaction)
