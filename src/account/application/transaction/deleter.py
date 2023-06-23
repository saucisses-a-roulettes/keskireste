from dataclasses import dataclass


from src.account.application.transaction.repository import TransactionRepository, TransactionNotFound
from src.account.domain.account import AccountId
from src.account.domain.transaction import TransactionId
from src.shared.application.repository import EntityNotFound


@dataclass(frozen=True)
class TransactionDeletionRequest:
    id: TransactionId


class TransactionDeleter:
    def __init__(self, repository: TransactionRepository) -> None:
        self._repository = repository

    def delete(self, request: TransactionDeletionRequest) -> None:
        try:
            self._repository.delete(request.id)
        except EntityNotFound as e:
            raise TransactionNotFound(transaction_id=request.id) from e
