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
import calendar
import datetime
import re
from abc import ABC, abstractmethod
from collections.abc import Iterator
from enum import IntEnum

import dateutil

from src.account.domain.account import AccountId
from src.shared.domain.entity import EntityBase, Id
from src.shared.domain.string import StringTooShort, StringTooLong, StringContainsInvalidCharacters
from src.shared.domain.value_object import ValueObject


class RecurringTransactionId(Id, ABC):
    pass


class RecurringTransactionName(ValueObject[str]):
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


class DailyFrequency(RecurringFrequency):
    def list_occurring_dates_between(self, start_date: datetime.date, end_date: datetime.date) -> list[datetime.date]:
        if end_date < start_date:
            raise ValueError("End date must be after the start date")
        return [start_date + datetime.timedelta(days=i) for i in range((end_date - start_date).days + 1)]


class DayEnum(IntEnum):
    MONDAY = 0
    TUESDAY = 1
    WEDNESDAY = 2
    THURSDAY = 3
    FRIDAY = 4
    SATURDAY = 5
    SUNDAY = 6


class WeeklyFrequency(RecurringFrequency):
    def __init__(self, day: DayEnum) -> None:
        self._day = day

    def list_occurring_dates_between(self, start_date: datetime.date, end_date: datetime.date) -> list[datetime.date]:
        if end_date < start_date:
            raise ValueError("End date must be after the start date")

        return [
            dt.date()
            for dt in dateutil.rrule.rrule(dateutil.rrule.DAILY, dtstart=start_date, until=end_date)
            if dt.weekday() == self._day
        ]


class MonthlyFrequency(RecurringFrequency):
    def __init__(self, day: int) -> None:
        if not 1 <= day <= 31:
            raise ValueError("Day must be an integer between 1 and 31")
        self._day = day

    def list_occurring_dates_between(self, start_date: datetime.date, end_date: datetime.date) -> list[datetime.date]:
        if end_date < start_date:
            raise ValueError("End date must be after the start date")

        return [
            current_date
            for current_date in self._generate_dates(start_date, end_date)
            if self._day <= self._last_day_of_month(current_date)
        ]

    @staticmethod
    def _generate_dates(start_date: datetime.date, end_date: datetime.date) -> Iterator[datetime.date]:
        current_date = start_date
        while current_date <= end_date:
            yield current_date
            current_date += datetime.timedelta(days=1)

    @staticmethod
    def _last_day_of_month(date: datetime.date) -> int:
        next_month = date.replace(day=28) + datetime.timedelta(days=4)
        return (next_month - datetime.timedelta(days=next_month.day)).day


class YearlyFrequency(RecurringFrequency):
    def __init__(self, day: int, month: int) -> None:
        if not 1 <= day <= 31:
            raise ValueError("Day must be an integer between 1 and 31")
        if not 1 <= month <= 12:
            raise ValueError("Month must be an integer between 1 and 12")
        self._day = day
        self._month = month

    def list_occurring_dates_between(self, start_date: datetime.date, end_date: datetime.date) -> list[datetime.date]:
        return [
            date
            for year in range(start_date.year, end_date.year + 1)
            for date in self._list_every_year_dates(year)
            if date and start_date <= date <= end_date
        ]

    def _list_every_year_dates(self, year: datetime.date.year) -> list[datetime.date]:
        return [
            datetime.date(year, self._month, self._day)
            if self._day
            <= (
                (calendar.monthrange(year, self._month)[1] if self._month != 2 else 29 if calendar.isleap(year) else 28)
            )
            else None
        ]


class RecurringTransaction(EntityBase[RecurringTransactionId]):
    def __init__(
        self,
        id_: RecurringTransactionId,
        account_id: AccountId,
        name: str,
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
    def name(self) -> str:
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
