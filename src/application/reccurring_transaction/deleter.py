from dataclasses import dataclass

from src.application.reccurring_transaction.repository import (
    RecurringTransactionRepository,
    RecurringTransactionNotFound,
)
from src.domain.recurring_transaction import RecurringTransactionId
from src.shared.application.repository import EntityNotFound


@dataclass(frozen=True)
class RecurringTransactionDeletionRequest:
    id: RecurringTransactionId


class RecurringTransactionDeleter:
    def __init__(self, repository: RecurringTransactionRepository) -> None:
        self._repository = repository

    def delete(self, request: RecurringTransactionDeletionRequest) -> None:
        try:
            self._repository.delete(request.id)
        except EntityNotFound as e:
            raise RecurringTransactionNotFound(recurring_transaction_id=request.id) from e
