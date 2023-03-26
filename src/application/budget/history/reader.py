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

from dataclasses import dataclass
from src.application.budget.history.repository import HistoryRepository
from src.application.exception import BadRequestException
from src.application.repository import CannotRetrieveEntity
from src.domain.entity import Id
from src.domain.history import Date, Operation, RecurrentOperation


@dataclass(frozen=True)
class HistoryReadResponse:
    date: Date
    recurrent_operations: set[RecurrentOperation]
    operations: set[Operation]


class HistoryReader:
    def __init__(self, repository: HistoryRepository) -> None:
        self._repository = repository

    def retrieve(self, id_: Id) -> HistoryReadResponse:
        try:
            history = self._repository.retrieve(id_)
        except CannotRetrieveEntity as err:
            raise BadRequestException(f"History `{id_}` not found") from err
        return HistoryReadResponse(
            date=history.date,
            recurrent_operations=history.recurrent_operations,
            operations=history.operations,
        )
