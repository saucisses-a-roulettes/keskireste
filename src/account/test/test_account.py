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
from src.shared.domain.entity import IdBase
from src.shared.domain.string import StringTooShort, StringTooLong, StringContainsInvalidCharacters
from src.shared.test.test_entity import MockId


class MockUserId(IdBase[str]):
    pass


def test_valid_account_name():
    account_name = AccountName("my_account")
    assert account_name.value == "my_account"


def test_invalid_account_name_too_short():
    with pytest.raises(StringTooShort):
        AccountName("abc")


def test_invalid_account_name_too_long():
    with pytest.raises(StringTooLong):
        AccountName("a" * 31)


def test_invalid_account_name_invalid_characters():
    with pytest.raises(StringContainsInvalidCharacters):
        AccountName("my_account!")


def test_account_creation():
    account_id = MockId("1")
    user_id = MockUserId("1")
    name = AccountName("my_account")
    account = Account(account_id, user_id, name)

    assert account.id == account_id
    assert account.user_id == user_id
    assert account.name == name


def test_rename():
    account_id = MockId("1")
    user_id = MockUserId("1")
    name = AccountName("my_account")
    new_name = AccountName("new_account")
    account = Account(account_id, user_id, name)

    account.rename(new_name)

    assert account.name == new_name
