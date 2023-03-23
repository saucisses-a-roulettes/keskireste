from dataclasses import dataclass, field
from src.application.budget.history.repository import HistoryRepository
from src.application.budget.repository import BudgetRepository
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
        deleted_recurrent_operation = history.recurrent_operations - request.recurrent_operations

        for op in new_recurrent_operation:
            history.add_recurrent_operation(op)
        for op in deleted_recurrent_operation:
            history.remove_recurrent_operation(op.name)

        for op in request.operations:
            history.add_operation(op)

        self._repository.update(history)
