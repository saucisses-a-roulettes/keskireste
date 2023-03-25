import contextlib
import dataclasses
import pickle
from typing import Self
from src.application.budget.history.repository import HistoryRepository
from src.application.repository import CannotRetrieveEntity
from src.domain.entity import Id
from src.domain.history import Date, History
from src.infrastructure.budget.repository.model import BudgetPath, BudgetPickleModel


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


class HistoryPickleRepository(HistoryRepository[HistoryId]):
    def retrieve(self, id_: HistoryId) -> History:
        with open(str(id_.budget_path), "rb") as f:
            model: BudgetPickleModel = pickle.load(f)

        try:
            return next(h for h in model.histories if h.id == id_)
        except StopIteration as err:
            raise CannotRetrieveEntity(id_) from err

    def create(self, history: History[HistoryId]) -> None:
        path = str(history.id.budget_path)
        with open(path, "rb") as f:
            model: BudgetPickleModel = pickle.load(f)
        new_histories = set(model.histories)
        new_histories.add(history)
        model = dataclasses.replace(model, histories=frozenset(new_histories))
        with open(path, "wb") as f:
            pickle.dump(model, f)

    def update(self, history: History[HistoryId]) -> None:
        path = str(history.id.budget_path)
        with open(path, "rb") as f:
            model: BudgetPickleModel = pickle.load(f)

        if history in model.histories:
            new_histories = set(model.histories)
            with contextlib.suppress(KeyError):
                new_histories.remove(history)
            new_histories.add(history)
            # print(new_histories)
            model = dataclasses.replace(model, histories=frozenset(new_histories))
            with open(path, "wb") as f:
                pickle.dump(model, f)
