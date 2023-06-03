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
import pytest

from src.account.domain.account import AccountName, Account
from src.account.test.domain.mocks import MockUserId, MockAccountId
from src.shared.domain.string import StringTooShort, StringTooLong, StringContainsInvalidCharacters


@pytest.fixture()
def sample_account():
    return Account(
        id_=MockAccountId("1"), user_id=MockUserId("1"), name=AccountName("my_account"), reference_balance=50.0
    )


def test_valid_account_name():
    account_name = AccountName("my_account")
    assert account_name == "my_account"


def test_invalid_account_name_too_short():
    with pytest.raises(StringTooShort):
        AccountName("abc")


def test_invalid_account_name_too_long():
    with pytest.raises(StringTooLong):
        AccountName("a" * 31)


def test_invalid_account_name_invalid_characters():
    with pytest.raises(StringContainsInvalidCharacters):
        AccountName("my_account!")


def test_account_creation(sample_account: Account):
    assert sample_account.id == MockAccountId("1")
    assert sample_account.user_id == MockUserId("1")
    assert sample_account.name == AccountName("my_account")
    assert sample_account.reference_balance == 50.0


def test_rename(sample_account: Account):
    new_name = AccountName("new_account")
    sample_account.rename(new_name)

    assert sample_account.name == new_name


def test_modify_reference_balance(sample_account: Account):
    new_reference_balance = 100.0
    sample_account.modify_reference_balance(new_reference_balance)

    assert sample_account.reference_balance == new_reference_balance
