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

from src.account.domain.account import UserId
from src.account.domain.transaction import Transaction
from src.shared.domain.entity import IdBase


class MockId(IdBase[str]):
    pass


class MockUserId(UserId, IdBase[str]):
    pass


@pytest.fixture
def sample_transaction():
    return Transaction(MockId("1"), MockUserId("1"), datetime.date(2022, 1, 1), "Sample Transaction", 100.0)


def test_transaction_properties(sample_transaction):
    assert sample_transaction.user_id == MockUserId("1")
    assert sample_transaction.date == datetime.date(2022, 1, 1)
    assert sample_transaction.label == "Sample Transaction"
    assert sample_transaction.amount == 100.0


def test_rectify_date(sample_transaction):
    new_date = datetime.date(2022, 2, 1)
    sample_transaction.rectify_date(new_date)
    assert sample_transaction.date == new_date


def test_rectify_amount(sample_transaction):
    new_amount = 200.0
    sample_transaction.rectify_amount(new_amount)
    assert sample_transaction.amount == new_amount


def test_modify_label(sample_transaction):
    new_label = "Updated Label"
    sample_transaction.modify_label(new_label)
    assert sample_transaction.label == new_label
