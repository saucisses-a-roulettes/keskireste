from src.application.history.repository import HistoryRepository
from src.domain.history import History


class HistoryCreator:
    def __init__(self, repository: HistoryRepository) -> None:
        self._repository = repository

    def create(self, path: str) -> None:
        history = History(
            path=path,
            monthly_incomes=set(),
            monthly_expenses=set(),
            operations=set(),
            filtered_operations=set(),
        )
        self._repository.save(history)
