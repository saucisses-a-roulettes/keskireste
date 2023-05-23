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
from typing import TypeVar, Generic

from shared.domain.value_object import ValueObject


class Id(ABC):
    @abstractmethod
    def __str__(self) -> str:
        pass

    @abstractmethod
    def __hash__(self):
        pass

    @abstractmethod
    def __eq__(self, other: object) -> bool:
        pass


TId = TypeVar("TId", bound=Id)


class IdBase(ValueObject, Id, ABC):
    pass


class Entity(ABC, Generic[TId]):
    @property
    @abstractmethod
    def id(self) -> TId:
        pass

    @abstractmethod
    def __hash__(self) -> int:
        pass

    @abstractmethod
    def __eq__(self, other: object) -> bool:
        pass


TEntity = TypeVar("TEntity", bound=Entity)


class EntityBase(Entity[TId]):
    def __init__(self, id_: TId):
        self._id = id_

    @property
    def id(self) -> TId:
        return self._id

    def __hash__(self) -> int:
        return hash(self.id)

    def __eq__(self, other: object) -> bool:
        return other.id == self.id if isinstance(other, Entity) else False
