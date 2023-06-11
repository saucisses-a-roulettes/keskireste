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

from src.account.domain.account import Account, AccountId
from src.shared.application.repository import EntityAlreadyExists, EntityNotFound
from src.shared.domain.entity import TId


class AccountAlreadyExists(EntityAlreadyExists, Generic[TId]):
    def __init__(self, account_id: TId) -> None:
        super().__init__(f"Account `{account_id}` already exists")
        self._account_id = account_id

    @property
    def account_id(self) -> TId:
        return self._account_id


class AccountNotFound(EntityNotFound, Generic[TId]):
    def __init__(self, account_id: TId) -> None:
        super().__init__(f"Account `{account_id}` not found")
        self._account_id = account_id

    @property
    def account_id(self) -> TId:
        return self._account_id


class AccountRepository(ABC):
    @abstractmethod
    def add(self, account: Account) -> None:
        """
        :param account:
        :raises AccountAlreadyExists
        """
        pass

    @abstractmethod
    def retrieve(self, id_: AccountId) -> None:
        """
        :param id_:
        :raises AccountNotFound
        """
        pass
