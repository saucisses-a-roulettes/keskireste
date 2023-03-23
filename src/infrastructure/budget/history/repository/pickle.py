import contextlib
import dataclasses
import pickle
from src.application.budget.history.repository import HistoryRepository
from src.domain.entity import Id
from src.domain.history import History
from src.infrastructure.budget.repository.model import BudgetPickleModel


class HistoryPickleRepository(HistoryRepository):
    def __init__(self, path_separator: str) -> None:
        self._path_separator = path_separator

    def retrieve(self, id_: Id) -> History:
        with open(str(id_), "rb") as f:
            model: BudgetPickleModel = pickle.load(f)

        return next(h for h in model.histories if h.id == id_)

    def create(self, history: History) -> None:
        path = str(history.id).split(self._path_separator)[0]
        with open(path, "rb") as f:
            model: BudgetPickleModel = pickle.load(f)

        new_histories = set(model.histories)
        new_histories.add(history)
        dataclasses.replace(model, histories=frozenset(new_histories))
        with open(path, "wb") as f:
            pickle.dump(model, f)

    def update(self, history: History) -> None:
        path = str(history.id).split(self._path_separator)[0]
        with open(path, "rb") as f:
            model: BudgetPickleModel = pickle.load(f)

        if history in model.histories:
            new_histories = set(model.histories)
            with contextlib.suppress(KeyError):
                new_histories.remove(history)
            new_histories.add(history)
            dataclasses.replace(model, histories=frozenset(new_histories))
            with open(path, "wb") as f:
                pickle.dump(model, f)
