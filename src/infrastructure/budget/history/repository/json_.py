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

import json
from typing import cast

from shared.application.shared import CannotRetrieveEntity

from src.application.budget.history.repository import HistoryRepository
from src.domain.history import Date, History, Operation, RecurrentOperation
from src.infrastructure.budget.history.repository.model import HistoryId
from src.infrastructure.budget.repository.json_ import (
    BudgetDictModel,
    HistoryDictModel,
    OperationDictModel,
    RecurrentOperationDictModel,
)
from src.infrastructure.budget.repository.model import BudgetPath


class HistoryJsonRepository(HistoryRepository[BudgetPath, HistoryId]):
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

    def list_by_budget(self, budget_id: BudgetPath) -> frozenset[History]:
        path = str(budget_id)
        with open(path, "r") as f:
            model = cast(BudgetDictModel, json.load(f))

        return frozenset(
            History(
                id_=HistoryId(budget_path=budget_id, date=Date(h["year"], h["month"])),
                date=Date(h["year"], h["month"]),
                recurrent_operations={RecurrentOperation(op["name"], op["value"]) for op in h["recurrent_operations"]},
                operations={Operation(op["id"], op["day"], op["name"], op["value"]) for op in h["operations"]},
            )
            for h in model["histories"]
        )

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
