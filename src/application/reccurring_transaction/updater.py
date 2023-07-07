from dataclasses import dataclass

from src.application.reccurring_transaction.repository import (
    RecurringTransactionRepository,
    RecurringTransactionNotFound,
)
from src.domain.account import AccountId
from src.domain.recurring_transaction import (
    RecurringTransactionId,
    RecurringTransactionName,
    RecurringFrequency,
)
from src.shared.application.repository import EntityNotFound


@dataclass(frozen=True)
class RecurringTransactionUpdateRequest:
    id: RecurringTransactionId
    account_id: AccountId
    name: RecurringTransactionName
    amount: float
    frequency: RecurringFrequency


class RecurringTransactionUpdater:
    def __init__(self, repository: RecurringTransactionRepository) -> None:
        self._repository = repository

    def update(self, request: RecurringTransactionUpdateRequest) -> None:
        try:
            recurring_transaction = self._repository.retrieve(request.id)
        except EntityNotFound as e:
            raise RecurringTransactionNotFound(recurring_transaction_id=request.id) from e

        recurring_transaction.rename(request.name)
        recurring_transaction.modify_amount(request.amount)
        recurring_transaction.modify_frequency(request.frequency)

        self._repository.update(recurring_transaction)
