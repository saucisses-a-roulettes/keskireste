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
from src.domain.history import Operation, RecurrentOperation


@dataclass(frozen=True)
class HistoryUpdateRequest:
    id_: Id
    recurrent_operations: set[RecurrentOperation]
    operations: set[Operation]


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

        new_operations = request.operations - history.operations
        existing_operations = history.operations & request.operations
        deleted_operations = history.operations - request.operations

        for op in new_operations:
            history.add_operation(op)
        for op in existing_operations:
            history.update_operation(op)
        for op in deleted_operations:
            history.remove_operation(op)

        self._repository.update(history)
