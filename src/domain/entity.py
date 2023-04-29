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
from typing import TypeVar, Type


class Id(ABC):
    @abstractmethod
    def __str__(self) -> str:
        pass

    @abstractmethod
    def __hash__(self):
        pass


TId = TypeVar("TId", bound=Id)


class EntityNotFound(Exception):
    def __init__(self, entity_type: Type, entity_id: Id) -> None:
        super().__init__(f"{entity_type} of id `{entity_id}` not found")
        self._entity_id = entity_id
        self._entity_type = entity_type

    @property
    def entity_type(self) -> Type:
        return self._entity_type

    @property
    def entity_id(self) -> Id:
        return self._entity_id
