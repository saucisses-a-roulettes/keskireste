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
from typing import Generic, TypeVar

from src.domain.entity import Id

TBudgetId = TypeVar("TBudgetId", bound=Id)


class Budget(Generic[TBudgetId]):
    def __init__(self, id_: TBudgetId, histories_ids: frozenset[TBudgetId]) -> None:
        self._id = id_
        self._histories_ids = histories_ids

    @property
    def id(self) -> TBudgetId:
        return self._id

    @property
    def histories_ids(self) -> frozenset[TBudgetId]:
        return self._histories_ids
