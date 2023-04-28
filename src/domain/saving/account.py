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
from typing import TypeVar, Generic

from src.domain.entity import Id

TSavingAccountId = TypeVar("TSavingAccountId", bound=Id)


class SavingAccount(Generic[TSavingAccountId]):
    def __init__(self, id_: TSavingAccountId, name: str, balance: float = 0) -> None:
        self._id = id_
        self._balance = balance
        self._name = name

    @property
    def name(self) -> str:
        return self.name

    @property
    def balance(self) -> float:
        return self.balance

    @property
    def id(self) -> TSavingAccountId:
        return self._id

    def rename(self, name: str) -> None:
        self._name = name

    def update_balance(self, balance: float) -> None:
        self._balance = balance
