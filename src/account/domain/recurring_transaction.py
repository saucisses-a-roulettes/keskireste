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
import re
from abc import ABC, abstractmethod
from collections.abc import Iterator
from dataclasses import dataclass
from enum import IntEnum

import dateutil.rrule

from src.account.domain.account import AccountId
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


class RecurringFrequency(ABC):
    @abstractmethod
    def list_occurring_dates_between(self, start_date: datetime.date, end_date: datetime.date) -> list[datetime.date]:
        pass


@dataclass(frozen=True)
class DailyFrequency(RecurringFrequency):
    def list_occurring_dates_between(self, start_date: datetime.date, end_date: datetime.date) -> list[datetime.date]:
        if end_date < start_date:
            raise ValueError("End date must be after the start date")
        return [start_date + datetime.timedelta(days=i) for i in range((end_date - start_date).days + 1)]


class Day(IntEnum):
    MONDAY = 0
    TUESDAY = 1
    WEDNESDAY = 2
    THURSDAY = 3
    FRIDAY = 4
    SATURDAY = 5
    SUNDAY = 6


@dataclass(frozen=True)
class WeeklyFrequency(RecurringFrequency):
    day: Day

    def list_occurring_dates_between(self, start_date: datetime.date, end_date: datetime.date) -> list[datetime.date]:
        if end_date < start_date:
            raise ValueError("End date must be after the start date")

        return [
            dt.date()
            for dt in dateutil.rrule.rrule(dateutil.rrule.DAILY, dtstart=start_date, until=end_date)
            if dt.weekday() == self.day
        ]


@dataclass(frozen=True)
class MonthlyFrequency(RecurringFrequency):
    day: int

    def __post_init__(self) -> None:
        if not 1 <= self.day <= 31:
            raise ValueError("Day must be an integer between 1 and 31")

    def list_occurring_dates_between(self, start_date: datetime.date, end_date: datetime.date) -> list[datetime.date]:
        if end_date < start_date:
            raise ValueError("End date must be after the start date")

        return [
            current_date for current_date in self._generate_dates(start_date, end_date) if current_date.day == self.day
        ]

    @staticmethod
    def _generate_dates(start_date: datetime.date, end_date: datetime.date) -> Iterator[datetime.date]:
        current_date = start_date
        while current_date <= end_date:
            yield current_date
            current_date += datetime.timedelta(days=1)


@dataclass(frozen=True)
class YearlyFrequency(RecurringFrequency):
    day: int
    month: int

    def __post_init__(self) -> None:
        if not 1 <= self.day <= 31:
            raise ValueError("Day must be an integer between 1 and 31")
        if not 1 <= self.month <= 12:
            raise ValueError("Month must be an integer between 1 and 12")

    def list_occurring_dates_between(self, start_date: datetime.date, end_date: datetime.date) -> list[datetime.date]:
        return [
            date
            for year in range(start_date.year, end_date.year + 1)
            for date in self._list_every_year_dates(year)
            if date.day == self.day and date.month == self.month
        ]

    @staticmethod
    def _list_every_year_dates(year: int) -> list[datetime.date]:
        start_date = datetime.date(year, 1, 1)
        end_date = datetime.date(year, 12, 31)

        return [date.date() for date in dateutil.rrule.rrule(dateutil.rrule.DAILY, dtstart=start_date, until=end_date)]


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
