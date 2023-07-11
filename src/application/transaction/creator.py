import datetime
from dataclasses import dataclass

from src.application.transaction.repository import TransactionRepository, TransactionAlreadyExists
from src.domain.transaction import AccountId, Transaction
from src.domain.transaction import TransactionId
from src.shared.application.id import IdFactory
from src.shared.application.repository import EntityAlreadyExists


@dataclass(frozen=True)
class TransactionCreationRequest:
    account_id: AccountId
    date: datetime.date
    label: str
    amount: float


class TransactionCreator:
    def __init__(self, repository: TransactionRepository, id_factory: IdFactory[TransactionId]) -> None:
        self._repository = repository
        self._id_factory = id_factory

    def create(self, request: TransactionCreationRequest) -> None:
        transaction = Transaction(
            id_=self._id_factory.generate_id(),
            account_id=request.account_id,
            date=request.date,
            label=request.label,
            amount=request.amount,
        )

        try:
            self._repository.add(transaction)
        except EntityAlreadyExists as e:
            raise TransactionAlreadyExists(transaction_id=transaction.id) from e
