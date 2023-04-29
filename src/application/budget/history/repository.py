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

from abc import ABC, abstractmethod
from typing import Generic

from src.domain.budget.budget import TBudgetId
from src.domain.budget.history import History, THistoryId


class HistoryRepository(ABC, Generic[TBudgetId, THistoryId]):
    @abstractmethod
    def retrieve(self, id_: THistoryId) -> History[THistoryId]:
        pass

    @abstractmethod
    def list_by_budget(self, budget_id: TBudgetId) -> frozenset[History]:
        pass

    @abstractmethod
    def create(self, history: History[THistoryId]) -> None:
        pass

    @abstractmethod
    def update(self, history: History[THistoryId]) -> None:
        pass
