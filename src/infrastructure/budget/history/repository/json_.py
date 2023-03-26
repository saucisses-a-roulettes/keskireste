import json
from typing import cast
from src.application.budget.history.repository import HistoryRepository
from src.application.repository import CannotRetrieveEntity
from src.domain.history import Date, History, Operation, RecurrentOperation
from src.infrastructure.budget.history.repository.model import HistoryId
from src.infrastructure.budget.repository.json_ import (
    BudgetDictModel,
    HistoryDictModel,
    OperationDictModel,
    RecurrentOperationDictModel,
)


class HistoryJsonRepository(HistoryRepository[HistoryId]):
    def retrieve(self, id_: HistoryId) -> History:
        path = str(id_.budget_path)
        with open(path, "r") as f:
            model = cast(BudgetDictModel, json.load(f))

        try:
            return next(
                History(
                    id_=HistoryId(budget_path=id_.budget_path, date=Date(h["year"], h["month"])),
                    date=Date(h["year"], h["month"]),
                    recurrent_operations={
                        RecurrentOperation(op["name"], op["value"]) for op in h["recurrent_operations"]
                    },
                    operations={Operation(op["id"], op["day"], op["name"], op["value"]) for op in h["operations"]},
                )
                for h in model["histories"]
                if HistoryId(id_.budget_path, Date(h["year"], h["month"])) == id_
            )
        except StopIteration as err:
            raise CannotRetrieveEntity(id_) from err

    def create(self, history: History[HistoryId]) -> None:
        path = str(history.id.budget_path)
        history_model = HistoryDictModel(
            year=history.date.year,
            month=history.date.month,
            recurrent_operations=[
                RecurrentOperationDictModel(name=op.name, value=op.value) for op in history.recurrent_operations
            ],
            operations=[
                OperationDictModel(id=str(op.id), day=op.day, name=op.name, value=op.value) for op in history.operations
            ],
        )
        with open(path, "r") as f:
            model = cast(BudgetDictModel, json.load(f))
        new_histories = model["histories"]
        new_histories.append(history_model)
        model["histories"] = list(new_histories)
        with open(path, "w") as f:
            json.dump(model, f)

    def update(self, history: History[HistoryId]) -> None:
        path = str(history.id.budget_path)
        history_model = HistoryDictModel(
            year=history.date.year,
            month=history.date.month,
            recurrent_operations=[
                RecurrentOperationDictModel(name=op.name, value=op.value) for op in history.recurrent_operations
            ],
            operations=[
                OperationDictModel(id=str(op.id), day=op.day, name=op.name, value=op.value) for op in history.operations
            ],
        )
        history_model_id = HistoryId(history.id.budget_path, Date(history_model["year"], history_model["month"]))
        with open(path, "r") as f:
            model = cast(BudgetDictModel, json.load(f))

        if history_model_id in (
            HistoryId(history.id.budget_path, Date(h["year"], h["month"])) for h in model["histories"]
        ):
            new_histories: list[HistoryDictModel] = [
                h
                for h in model["histories"]
                if HistoryId(history.id.budget_path, Date(h["year"], h["month"])) != history_model_id
            ] + [history_model]
            model["histories"] = new_histories
            with open(path, "w") as f:
                json.dump(model, f)
