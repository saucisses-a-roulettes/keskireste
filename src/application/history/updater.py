from dataclasses import dataclass
from src.application.history.repository import HistoryRepository
from src.domain.history import Operation, RecurrentOperation


@dataclass(frozen=True)
class HistoryUpdateRequest:
    path: str
    recurrent_operations: set[RecurrentOperation]
    operations: set[Operation]


class HistoryUpdater:
    def __init__(self, repository: HistoryRepository) -> None:
        self._repository = repository

    def update(self, request: HistoryUpdateRequest) -> None:
        history = self._repository.retrieve(request.path)

        new_recurrent_operation = request.recurrent_operations - history.recurrent_incomes - history.recurrent_expenses
        deleted_recurrent_operation = (
            history.recurrent_incomes | history.recurrent_expenses
        ) - request.recurrent_operations

        for i in new_recurrent_operation:
            history.add_recurrent_operation(i)
        for i in deleted_recurrent_operation:
            history.remove_recurrent_operation(i)

        for op in request.operations:
            history.add_operation(op)

        self._repository.save(history)
