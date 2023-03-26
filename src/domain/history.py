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

import pathlib
from dataclasses import dataclass
from typing import Generic, Self
from src.domain.entity import Id, TId


class RecurrentOperationAlreadyExist(Exception):
    def __init__(self, name: str) -> None:
        super().__init__(f"Recurrent operation `{name}` already exists")


class RecurrentOperationNotFound(Exception):
    def __init__(self, name: str) -> None:
        super().__init__(f"Recurrent operation `{name}` not found")


class Path:
    def __init__(self, value: str) -> None:
        if value.startswith("~/"):
            value = value.replace("~", str(pathlib.Path.home()), 1)
        self._value = value

    @property
    def value(self) -> str:
        return self._value

    def __str__(self) -> str:
        return self._value

    @property
    def name(self) -> str:
        return self.value.split("/")[-1]


@dataclass(frozen=True)
class RecurrentOperation:
    name: str
    value: float

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other: Self) -> bool:
        return self.name == other.name


@dataclass(frozen=True)
class Operation:
    id: str
    day: int
    name: str
    value: float

    def __post_init__(self):
        if self.day < 0 or self.day > 31:
            raise ValueError(f"Day `{self.day}` is invalid")


@dataclass(frozen=True)
class Date:
    year: int
    month: int

    def __post_init__(self):
        if self.year < 0:
            raise ValueError(f"Year {self.year} cannot be negative")
        if self.month < 1 or self.month > 12:
            raise ValueError(f"Month `{self.month}` is invalid")


class History(Generic[TId]):
    def __init__(
        self, id_: TId, date: Date, recurrent_operations: set[RecurrentOperation], operations: set[Operation]
    ) -> None:
        self._id = id_
        self._date = date
        self._recurrent_operations = recurrent_operations
        self._operations = operations

    def __hash__(self):
        return hash(self._id)

    def __eq__(self, o: Self) -> bool:
        return self.id == o.id

    @property
    def id(self) -> TId:
        return self._id

    @property
    def date(self) -> Date:
        return self._date

    @property
    def recurrent_operations(self) -> set[RecurrentOperation]:
        return self._recurrent_operations

    @property
    def operations(self) -> set[Operation]:
        return self._operations

    def add_recurrent_operation(self, op: RecurrentOperation) -> None:
        if op in self._recurrent_operations:
            raise RecurrentOperationAlreadyExist(op.name)
        self._recurrent_operations.add(op)

    def remove_recurrent_operation(self, name: str) -> None:
        try:
            op = next(o for o in self._recurrent_operations if o.name == name)
        except StopIteration as err:
            raise RecurrentOperationNotFound(name) from err
        self._recurrent_operations.remove(op)

    def add_operation(self, op: Operation) -> None:
        if not any(op.name.startswith(r_op.name) for r_op in self._recurrent_operations):
            self._operations.add(op)
