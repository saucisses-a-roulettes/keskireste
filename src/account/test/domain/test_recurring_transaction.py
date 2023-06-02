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

import pytest

from src.account.domain.recurring_transaction import (
    DailyFrequency,
    RecurringTransaction,
    RecurringTransactionName,
    WeeklyFrequency,
    Day,
    MonthlyFrequency,
    YearlyFrequency,
)
from src.account.test.domain.mocks import RecurringTransactionMockId, MockAccountId
from src.shared.domain.string import StringTooShort, StringTooLong, StringContainsInvalidCharacters


class TestRecurringTransactionName:
    def test_invalid_recurring_transaction_name_too_short(self):
        with pytest.raises(StringTooShort):
            RecurringTransactionName("a")

    def test_invalid_recurring_transaction_name_too_long(self):
        with pytest.raises(StringTooLong):
            RecurringTransactionName("a" * 81)

    def test_invalid_recurring_transaction_name_invalid_characters(self):
        with pytest.raises(StringContainsInvalidCharacters):
            RecurringTransactionName("my_recurring_transaction!")


class TestRecurringFrequency:
    def test_daily_frequency_list_occurring_dates_between(self):
        start_date = datetime.date(2023, 1, 1)
        end_date = datetime.date(2023, 1, 3)
        expected_dates = [
            datetime.date(2023, 1, 1),
            datetime.date(2023, 1, 2),
            datetime.date(2023, 1, 3),
        ]

        daily_frequency = DailyFrequency()
        occurring_dates = daily_frequency.list_occurring_dates_between(start_date, end_date)

        assert occurring_dates == expected_dates

    def test_weekly_frequency_list_occurring_dates_between(self):
        start_date = datetime.date(2023, 1, 1)
        end_date = datetime.date(2023, 1, 31)
        expected_dates = [
            datetime.date(2023, 1, 1),
            datetime.date(2023, 1, 8),
            datetime.date(2023, 1, 15),
            datetime.date(2023, 1, 22),
            datetime.date(2023, 1, 29),
        ]

        weekly_frequency = WeeklyFrequency(Day.SUNDAY)
        occurring_dates = weekly_frequency.list_occurring_dates_between(start_date, end_date)

        assert occurring_dates == expected_dates

    def test_monthly_frequency_list_occurring_dates_between(self):
        start_date = datetime.date(2023, 1, 1)
        end_date = datetime.date(2023, 3, 31)
        expected_dates = [
            datetime.date(2023, 1, 1),
            datetime.date(2023, 2, 1),
            datetime.date(2023, 3, 1),
        ]

        monthly_frequency = MonthlyFrequency(1)
        occurring_dates = monthly_frequency.list_occurring_dates_between(start_date, end_date)

        assert occurring_dates == expected_dates

    def test_yearly_frequency_list_occurring_dates_between(self):
        start_date = datetime.date(2023, 1, 1)
        end_date = datetime.date(2025, 12, 31)
        expected_dates = [
            datetime.date(2023, 1, 1),
            datetime.date(2024, 1, 1),
            datetime.date(2025, 1, 1),
        ]

        yearly_frequency = YearlyFrequency(1, 1)
        occurring_dates = yearly_frequency.list_occurring_dates_between(start_date, end_date)

        assert occurring_dates == expected_dates


@pytest.fixture
def sample_transaction():
    return RecurringTransaction(
        id_=RecurringTransactionMockId("1"),
        account_id=MockAccountId("1"),
        name=RecurringTransactionName("sample-transaction"),
        amount=50.0,
        frequency=DailyFrequency(),
    )


class TestRecurringTransaction:
    def test_recurring_transaction_properties(self, sample_transaction: RecurringTransaction):
        assert sample_transaction.id == RecurringTransactionMockId("1")
        assert sample_transaction.account_id == MockAccountId("1")
        assert sample_transaction.name == "sample-transaction"
        assert sample_transaction.amount == 50.0
        assert sample_transaction.frequency == DailyFrequency()

    def test_recurring_transaction_rename(self, sample_transaction: RecurringTransaction):
        new_name = RecurringTransactionName("new-transaction-name")
        sample_transaction.rename(new_name)

        assert sample_transaction.name == new_name

    def test_recurring_transaction_modify_amount(self, sample_transaction: RecurringTransaction):
        new_amount = 100.0
        sample_transaction.modify_amount(new_amount)

        assert sample_transaction.amount == new_amount

    def test_recurring_transaction_modify_frequency(self, sample_transaction: RecurringTransaction):
        new_frequency = WeeklyFrequency(Day.MONDAY)
        sample_transaction.modify_frequency(new_frequency)

        assert sample_transaction.frequency == new_frequency
