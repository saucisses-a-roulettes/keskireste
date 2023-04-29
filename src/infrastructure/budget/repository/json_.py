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

import json as json_
from typing import TypedDict, cast

from src.application.budget.repository import BudgetRepository
from src.domain.budget.budget import Budget
from src.domain.budget.history import Date
from src.domain.entity import Id
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
