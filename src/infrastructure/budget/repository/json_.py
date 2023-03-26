import json as json_
from typing import TypedDict, cast
from src.application.budget.repository import BudgetRepository
from src.domain.budget import Budget
from src.domain.entity import Id
from src.domain.history import Date
from src.infrastructure.budget.history.repository.model import HistoryId
from src.infrastructure.budget.repository.model import BudgetPath


class RecurrentOperationDictModel(TypedDict):
    name: str
    value: float


class OperationDictModel(TypedDict):
    id: str
    day: int
    name: str
    value: float


class HistoryDictModel(TypedDict):
    year: int
    month: int
    recurrent_operations: list[RecurrentOperationDictModel]
    operations: list[OperationDictModel]


class BudgetDictModel(TypedDict):
    histories: list[HistoryDictModel]


class BudgetJsonRepository(BudgetRepository):
    def retrieve(self, id_: Id) -> Budget:
        with open(str(id_), "r") as f:
            model = cast(BudgetDictModel, json_.load(f))
        return Budget(
            id_=id_,
            histories_ids=frozenset(
                {HistoryId(BudgetPath(str(id_)), Date(h["year"], h["month"])) for h in model["histories"]}
            ),
        )

    def create(self, budget: Budget) -> None:
        model = BudgetDictModel(histories=[])
        with open(str(budget.id), "w") as f:
            json_.dump(model, f)
