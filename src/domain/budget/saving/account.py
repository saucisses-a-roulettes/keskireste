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
import datetime
from dataclasses import dataclass
from typing import TypeVar, Generic

from src.domain.budget.history import Date
from src.domain.entity import Id

TSavingAccountId = TypeVar("TSavingAccountId", bound=Id)


@dataclass(frozen=True)
class BalanceReference:
    balance: float
    date: Date


class SavingAccount(Generic[TSavingAccountId]):
    def __init__(self, id_: TSavingAccountId, name: str, balance: BalanceReference | None = None) -> None:
        self._id = id_
        self._balance_reference = balance or BalanceReference(
            0, Date(datetime.datetime.now().year, datetime.datetime.now().month)
        )
        self._name = name

    @property
    def id(self) -> TSavingAccountId:
        return self._id

    @property
    def name(self) -> str:
        return self.name

    @property
    def balance_reference(self) -> BalanceReference:
        return self._balance_reference

    def rename(self, name: str) -> None:
        self._name = name

    def update_balance_reference(self, balance_reference: BalanceReference) -> None:
        self._balance_reference = balance_reference
