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

from shared.domain.entity import TEntity, Id


class CannotRetrieveEntity(Exception):
    def __init__(self, id_: Id) -> None:
        super().__init__(f"Cannot retrieve entity `{id_}`")


class EntityAlreadyExists(Exception):
    def __init__(self, id_: Id) -> None:
        super().__init__(f"Entity `{id_}` already exists")


class Repository(ABC, Generic[TEntity]):
    @abstractmethod
    def add(self, entity: TEntity) -> None:
        pass

    @abstractmethod
    def retrieve(self, id_: str) -> TEntity:
        pass

    @abstractmethod
    def update(self, entity: TEntity) -> None:
        pass

    @abstractmethod
    def delete(self, id_: str) -> None:
        pass

    @abstractmethod
    def all(self) -> list[TEntity]:
        pass
