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

from src.shared.domain.email import EmailAddress
from src.shared.domain.string import StringTooShort, StringTooLong, StringContainsInvalidCharacters
from src.shared.test.domain.test_entity import MockId
from src.user.domain.user import UserName, User


def test_valid_user_name():
    username = UserName("john_doe123")
    assert username.value == "john_doe123"


def test_invalid_user_name_too_short():
    with pytest.raises(StringTooShort):
        UserName("abc")


def test_invalid_user_name_too_long():
    with pytest.raises(StringTooLong):
        UserName("a" * 31)


def test_invalid_user_name_invalid_characters():
    with pytest.raises(StringContainsInvalidCharacters):
        UserName("john_doe!")


def test_user_creation():
    user_id = MockId("1")
    email = EmailAddress("john@example.com")
    username = UserName("john_doe")
    user = User(user_id, email, username)

    assert user.id == user_id
    assert user.email == email
    assert user.username == username


def test_change_email():
    user_id = MockId("1")
    email = EmailAddress("john@example.com")
    new_email = EmailAddress("johndoe@example.com")
    username = UserName("john_doe")
    user = User(user_id, email, username)

    user.change_email(new_email)

    assert user.email == new_email


def test_rename():
    user_id = MockId("1")
    email = EmailAddress("john@example.com")
    username = UserName("john_doe")
    new_username = UserName("johndoe")
    user = User(user_id, email, username)

    user.rename(new_username)

    assert user.username == new_username
