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
from typing import Generic

from src.application.budget.history.repository import HistoryRepository
from src.domain.budget.history import (
    RecurrentOperation,
    SavingTransactionAspects,
    LoanTransactionAspects,
    THistoryId,
    Operation,
)


@dataclass(frozen=True)
class RecurrentOperationsUpdateRequest(Generic[THistoryId]):
    history_id: THistoryId
    operations: set[RecurrentOperation]


@dataclass(frozen=True)
class OperationUpdateRequest:
    id: str
    day: int
    name: str
    amount: float
    transaction_aspects: SavingTransactionAspects | LoanTransactionAspects | None = None


@dataclass(frozen=True)
class OperationsUpdateRequest(Generic[THistoryId]):
    history_id: THistoryId
    operations: set[OperationUpdateRequest]


class HistoryUpdater:
    def __init__(self, repository: HistoryRepository) -> None:
        self._repository = repository

    def update_recurrent_operations(self, request: RecurrentOperationsUpdateRequest) -> None:
        history = self._repository.retrieve(request.history_id)

        new_recurrent_operation = request.operations - history.recurrent_operations
        existing_recurrent_operations = history.recurrent_operations & request.operations
        deleted_recurrent_operation = history.recurrent_operations - request.operations

        for r_op in new_recurrent_operation:
            history.add_recurrent_operation(r_op)
        for r_op in existing_recurrent_operations:
            history.update_recurrent_operation(r_op)
        for r_op in deleted_recurrent_operation:
            history.remove_recurrent_operation(r_op.name)

        self._repository.update(history)

    def update_operations(self, request: OperationsUpdateRequest) -> None:
        history = self._repository.retrieve(request.history_id)

        request_operations: set[Operation] = {
            Operation(
                id_=op.id,
                day=op.day,
                name=op.name,
                amount=op.amount,
                transaction_aspects=op.transaction_aspects,
            )
            for op in request.operations
        }

        current_operation_ids = {op.id for op in history.operations}
        input_operation_ids = {op.id for op in request_operations}

        new_operations = {op for op in request_operations if op.id not in current_operation_ids}
        existing_operations = {op for op in request_operations if op.id in current_operation_ids}
        deleted_operations = {op for op in history.operations if op.id not in input_operation_ids}

        for op in new_operations:
            history.add_operation(op)

        for op in existing_operations:
            history.rename_operation(op.id, op.name)
            history.modify_operation_amount(op.id, op.amount)

            if isinstance(op.transaction_aspects, SavingTransactionAspects):
                history.categorize_operation_as_saving_account_transaction(op.id, op.transaction_aspects)
            elif isinstance(op.transaction_aspects, LoanTransactionAspects):
                history.categorize_operation_as_loan_transaction(op.id, op.transaction_aspects)
            else:
                history.uncategorize_operation_as_saving_account_transaction(op.id)

        for op in deleted_operations:
            history.remove_operation(op.id)

        self._repository.update(history)
