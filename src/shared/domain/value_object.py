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
from abc import ABC
from typing import Generic, TypeVar

T = TypeVar("T")


class ValueObject(ABC, Generic[T]):
    def __init__(self, value: T) -> None:
        self._value = value
        self.__post_init__()

    def __post_init__(self) -> None:
        pass

    @property
    def value(self) -> T:
        return self._value

    def __eq__(self, other: object) -> bool:
        return self.__dict__ == other.__dict__ if isinstance(other, self.__class__) else False

    def __hash__(self) -> int:
        return hash(tuple(sorted(self.__dict__.items())))

    def __str__(self) -> str:
        return str(self._value)


class StringObject(ValueObject[str]):
    def __eq__(self, other: object) -> bool:
        if isinstance(other, ValueObject):
            return super().__eq__(other)
        elif isinstance(other, str):
            return self.value == other

        return False

    def __hash__(self):
        return self.value.__hash__()
