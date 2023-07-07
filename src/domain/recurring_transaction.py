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
import re
from abc import ABC
from dataclasses import dataclass
from enum import IntEnum

from src.domain.account import AccountId
from src.shared.domain.entity import EntityBase, Id
from src.shared.domain.string import StringTooShort, StringTooLong, StringContainsInvalidCharacters
from src.shared.domain.value_object import StringObject


class RecurringTransactionId(Id, ABC):
    pass


class RecurringTransactionName(StringObject):
    def __post_init__(self):
        if len(self.value) < 2:
            raise StringTooShort(self.value)
        if len(self.value) > 80:
            raise StringTooLong(self.value)
        if not re.match(r"^[a-zA-Z0-9_-]+$", self.value):
            raise StringContainsInvalidCharacters(self.value)


@dataclass(frozen=True)
class DailyFrequency:
    pass


class Day(IntEnum):
    MONDAY = 0
    TUESDAY = 1
    WEDNESDAY = 2
    THURSDAY = 3
    FRIDAY = 4
    SATURDAY = 5
    SUNDAY = 6


@dataclass(frozen=True)
class WeeklyFrequency:
    day: Day


@dataclass(frozen=True)
class MonthlyFrequency:
    day: int

    def __post_init__(self) -> None:
        if not 1 <= self.day <= 31:
            raise ValueError("Day must be an integer between 1 and 31")


@dataclass(frozen=True)
class YearlyFrequency:
    day: int
    month: int

    def __post_init__(self) -> None:
        if not 1 <= self.day <= 31:
            raise ValueError("Day must be an integer between 1 and 31")
        if not 1 <= self.month <= 12:
            raise ValueError("Month must be an integer between 1 and 12")


RecurringFrequency = DailyFrequency | WeeklyFrequency | MonthlyFrequency | YearlyFrequency


class RecurringTransaction(EntityBase[RecurringTransactionId]):
    def __init__(
        self,
        id_: RecurringTransactionId,
        account_id: AccountId,
        name: RecurringTransactionName,
        amount: float,
        frequency: RecurringFrequency,
    ) -> None:
        super().__init__(id_)
        self._account_id = account_id
        self._name = name
        self._amount = amount
        self._frequency = frequency

    @property
    def account_id(self) -> AccountId:
        return self._account_id

    @property
    def name(self) -> RecurringTransactionName:
        return self._name

    @property
    def amount(self) -> float:
        return self._amount

    @property
    def frequency(self) -> RecurringFrequency:
        return self._frequency

    def rename(self, new_name: RecurringTransactionName) -> None:
        self._name = new_name

    def modify_amount(self, new_amount: float) -> None:
        self._amount = new_amount

    def modify_frequency(self, new_frequency: RecurringFrequency) -> None:
        self._frequency = new_frequency
