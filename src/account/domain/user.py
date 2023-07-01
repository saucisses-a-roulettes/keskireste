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

from src.shared.domain.email import EmailAddress
from src.shared.domain.entity import EntityBase, Id
from src.shared.domain.string import StringTooLong, StringTooShort, StringContainsInvalidCharacters
from src.shared.domain.value_object import ValueObject


class UserId(Id, ABC):
    pass


class UserName(ValueObject[str]):
    def __post_init__(self):
        if len(self.value) < 4:
            raise StringTooShort(self.value)
        if len(self.value) > 30:
            raise StringTooLong(self.value)
        if not re.match(r"^[a-zA-Z0-9_-]+$", self.value):
            raise StringContainsInvalidCharacters(self.value)


class User(EntityBase[UserId]):
    def __init__(self, id_: UserId, email_address: EmailAddress, username: UserName) -> None:
        super().__init__(id_=id_)
        self._email_address = email_address
        self._username = username

    @property
    def email_address(self) -> EmailAddress:
        return self._email_address

    @property
    def username(self) -> UserName:
        return self._username

    def change_email_address(self, new_email: EmailAddress) -> None:
        self._email_address = new_email

    def rename(self, new_username: UserName) -> None:
        self._username = new_username
