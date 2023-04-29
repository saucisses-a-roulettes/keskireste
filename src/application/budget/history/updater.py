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

from src.application.budget.history.repository import HistoryRepository
from src.domain.entity import Id
from src.domain.history import RecurrentOperation, SavingTransactionAspects, LoanTransactionAspects


@dataclass(frozen=True)
class OperationUpdateRequest:
    id: str
    day: int
    name: str
    amount: float
    transaction_aspects: SavingTransactionAspects | LoanTransactionAspects | None = None


@dataclass(frozen=True)
class HistoryUpdateRequest:
    id_: Id
    recurrent_operations: set[RecurrentOperation]
    operations: set[OperationUpdateRequest]


class HistoryUpdater:
    def __init__(self, repository: HistoryRepository) -> None:
        self._repository = repository

    def update(self, request: HistoryUpdateRequest) -> None:
        history = self._repository.retrieve(request.id_)

        new_recurrent_operation = request.recurrent_operations - history.recurrent_operations
        existing_recurrent_operations = history.recurrent_operations & request.recurrent_operations
        deleted_recurrent_operation = history.recurrent_operations - request.recurrent_operations

        for r_op in new_recurrent_operation:
            history.add_recurrent_operation(r_op)
        for r_op in existing_recurrent_operations:
            history.update_recurrent_operation(r_op)
        for r_op in deleted_recurrent_operation:
            history.remove_recurrent_operation(r_op.name)

        current_operation_ids = {op.id for op in history.operations}
        input_operation_ids = {op.id for op in request.operations}

        new_operations = {op for op in request.operations if op.id not in current_operation_ids}
        existing_operations = {op for op in request.operations if op.id in current_operation_ids}
        deleted_operations = {op for op in history.operations if op.id not in input_operation_ids}

        for op in new_operations:
            history.add_operation(op)

        for op in existing_operations:
            history.rename_operation(op.id, op.name)
            history.modify_operation_amount(op.id, op.value)

            transaction_type = type(op.transaction_aspects)
            if transaction_type == SavingTransactionAspects:
                history.categorize_operation_as_saving_account_transaction(op.id, op.transaction_aspects)
            elif transaction_type == LoanTransactionAspects:
                history.categorize_operation_as_loan_transaction(op.id, op.transaction_aspects)
            else:
                history.uncategorize_operation_as_saving_account_transaction(op.id)

        for op in deleted_operations:
            history.remove_operation(op)

        self._repository.update(history)
