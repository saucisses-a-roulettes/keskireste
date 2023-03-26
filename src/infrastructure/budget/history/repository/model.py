from typing import Self
from src.domain.entity import Id
from src.domain.history import Date
from src.infrastructure.budget.repository.model import BudgetPath
class HistoryId(Id):
    def __init__(self, budget_path: BudgetPath, date: Date):
        self._budget_path = budget_path
        self._date = date

    @property
    def budget_path(self) -> BudgetPath:
        return self._budget_path

    @property
    def date(self) -> Date:
        return self._date

    def __str__(self) -> str:
        return f"{self.date.year}/{self.date.month}"

    def __hash__(self):
        return hash(self._date)

    def __eq__(self, other: Self) -> bool:
        return self.date == other.date
