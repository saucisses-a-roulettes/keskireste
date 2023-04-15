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
from typing import Generic

from src.domain.entity import TId


class Budget(Generic[TId]):
    def __init__(self, id_: TId, histories_ids: frozenset[TId]) -> None:
        self._id = id_
        self._histories_ids = histories_ids

    @property
    def id(self) -> TId:
        return self._id

    @property
    def histories_ids(self) -> frozenset[TId]:
        return self._histories_ids
