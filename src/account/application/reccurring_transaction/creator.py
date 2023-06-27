#  /*
#   * Copyright (c) 2023 Gael Monachon
#   *
#   * This program is free software: you can redistribute it and/or modify
#   * it under the terms of the GNU General Public License as published by
#   * the Free Software Foundation, either version 3 of the License, or
#   * (at your option) any later version.
#   *
#   * This program is distributed in the hope that it will be useful,
#   * but WITHOUT ANY WARRANTY; without even the implied warranty of
#   * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   * GNU General Public License for more details.
#   *
#   * You should have received a copy of the GNU General Public License
#   * along with this program.  If not, see <https://www.gnu.org/licenses/>.
#   */
from dataclasses import dataclass

from src.account.application.reccurring_transaction.repository import (
    RecurringTransactionAlreadyExists,
    RecurringTransactionRepository,
)
from src.account.domain.account import AccountId
from src.account.domain.recurring_transaction import (
    RecurringTransactionId,
    RecurringTransactionName,
    RecurringFrequency,
    RecurringTransaction,
)
from src.shared.application.repository import EntityAlreadyExists


@dataclass(frozen=True)
class RecurringTransactionCreationRequest:
    id: RecurringTransactionId
    account_id: AccountId
    name: RecurringTransactionName
    amount: float
    frequency: RecurringFrequency


class RecurringTransactionCreator:
    def __init__(self, repository: RecurringTransactionRepository) -> None:
        self._repository = repository

    def create(self, request: RecurringTransactionCreationRequest) -> None:
        recurring_transaction = RecurringTransaction(
            id_=request.id,
            account_id=request.account_id,
            name=request.name,
            amount=request.amount,
            frequency=request.frequency,
        )

        try:
            self._repository.add(recurring_transaction)
        except EntityAlreadyExists as e:
            raise RecurringTransactionAlreadyExists(recurring_transaction_id=request.id) from e
