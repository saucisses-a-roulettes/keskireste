from dataclasses import dataclass
from src.domain.history import History as DHistory, Operation, RecurrentOperation
from src.application.history.repository import HistoryRepository


@dataclass(frozen=True)
class History:
    path: str
    monthly_incomes: set[RecurrentOperation]
    monthly_expenses: set[RecurrentOperation]
    operations: set[Operation]
    filtered_operations: set[str]


class HistoryReader:
    def __init__(self, repository: HistoryRepository) -> None:
        self._repository = repository

    def retrieve(self, path: str) -> History:
        history: DHistory = self._repository.retrieve(path)

        return History(
            path=history.path,
            monthly_incomes=history.monthly_incomes,
            monthly_expenses=history.monthly_expenses,
            operations=history.operations,
            filtered_operations=history.filtered_operations,
        )
