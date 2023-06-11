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

from src.shared.application.repository import EntityAlreadyExists, EntityNotFound
from src.shared.domain.entity import TId
from src.user.domain.user import User


class UserAlreadyExists(EntityAlreadyExists, Generic[TId]):
    def __init__(self, user_id: TId) -> None:
        super().__init__(f"User `{user_id}` already exists")
        self._user_id = user_id

    @property
    def user_id(self) -> TId:
        return self._user_id


class UserNotFound(EntityNotFound, Generic[TId]):
    def __init__(self, user_id: TId) -> None:
        super().__init__(f"User `{user_id}` not found")
        self._user_id = user_id

    @property
    def user_id(self) -> TId:
        return self._user_id


class UserRepository(ABC, Generic[TId]):
    @abstractmethod
    def add(self, user: User) -> None:
        """
        :param user:
        :raises EntityAlreadyExists
        """
        pass

    @abstractmethod
    def retrieve(self, id_: TId) -> User:
        """
        :param id_:
        :return: User
        :raises EntityNotFound
        """
        pass

    @abstractmethod
    def update(self, user: User) -> None:
        """
        :param user:
        :raises EntityNotFound
        """
        pass

    @abstractmethod
    def delete(self, id_: TId) -> None:
        """
        :param id_:
        :return: EntityNotFound
        """
