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

from src.shared.domain.entity import TId, Id, EntityBase
from src.shared.domain.string import StringTooShort, StringTooLong, StringContainsInvalidCharacters
from src.shared.domain.value_object import ValueObject


class UserId(Id, ABC):
    pass


class AccountName(ValueObject[str]):
    def __post_init__(self):
        if len(self.value) < 4:
            raise StringTooShort(self.value)
        if len(self.value) > 30:
            raise StringTooLong(self.value)
        if not re.match(r"^[a-zA-Z0-9_-]+$", self.value):
            raise StringContainsInvalidCharacters(self.value)


class Account(EntityBase[TId]):
    def __init__(self, id_: TId, user_id: UserId, name: AccountName) -> None:
        super().__init__(id_)
        self._user_id = user_id
        self._name = name

    @property
    def user_id(self) -> UserId:
        return self._user_id

    @property
    def name(self) -> AccountName:
        return self._name

    def rename(self, new_name: AccountName) -> None:
        self._name = new_name
