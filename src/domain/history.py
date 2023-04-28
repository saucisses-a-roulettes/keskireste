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
import dataclasses
import pathlib
from dataclasses import dataclass
from functools import total_ordering
from typing import Generic, Self, TypeVar

from src.domain.entity import Id
from src.domain.saving.account import TSavingAccountId


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

    def __eq__(self, other: object) -> bool:
        if isinstance(other, RecurrentOperation):
            return self.name == other.name
        return False


class Operation:
    def __init__(
        self, id_: str, day: int, name: str, value: float, saving_account_id: TSavingAccountId | None = None
    ) -> None:
        if day < 0 or day > 31:
            raise ValueError(f"Day `{day}` is invalid")
        self._id = id_
        self._day = day
        self._name = name
        self._value = value
        self._saving_account_id = saving_account_id

    @property
    def id(self) -> str:
        return self.id

    @property
    def day(self) -> int:
        return self.day

    @property
    def name(self) -> str:
        return self.name

    @property
    def value(self) -> float:
        return self.value

    @property
    def saving_account_id(self) -> TSavingAccountId:
        return self._saving_account_id

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other: object) -> bool:
        return other.id == self.id if isinstance(other, Operation) else False

    def categorize_as_saving_deposit(self, saving_account_id: TSavingAccountId) -> None:
        self._saving_account_id = saving_account_id

    def uncategorize_as_saving_deposit(self) -> None:
        self._saving_account_id = None


@total_ordering
@dataclass(frozen=True)
class Date:
    year: int
    month: int

    @property
    def previous(self) -> Self:
        new_month = self.month - 1
        new_year = self.year
        if new_month < 1:
            new_year = self.year - 1
            new_month = 12
        return dataclasses.replace(self, year=new_year, month=new_month)

    def __post_init__(self):
        if self.year < 0:
            raise ValueError(f"Year {self.year} cannot be negative")
        if self.month < 1 or self.month > 12:
            raise ValueError(f"Month `{self.month}` is invalid")

    def __eq__(self, other: object) -> bool:
        return (self.year, self.month) == (other.year, other.month) if isinstance(other, Date) else False

    def __lt__(self, other: object) -> bool:
        return (self.year, self.month) < (other.year, other.month) if isinstance(other, Date) else False


THistoryId = TypeVar("THistoryId", bound=Id)


class OperationNotFound(Exception):
    def __init__(self, operation_id: str) -> None:
        super().__init__(f"Operation of id `{operation_id}` not found")
        self._operation_id = operation_id

    @property
    def operation_id(self) -> str:
        return self._operation_id


class History(Generic[THistoryId]):
    def __init__(
        self, id_: THistoryId, date: Date, recurrent_operations: set[RecurrentOperation], operations: set[Operation]
    ) -> None:
        self._id = id_
        self._date = date
        self._recurrent_operations = recurrent_operations
        self._operations = operations

    def __hash__(self):
        return hash(self._id)

    def __eq__(self, o: object) -> bool:
        return self.id == o.id if isinstance(o, History) else False

    @property
    def id(self) -> THistoryId:
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

    @property
    def balance(self) -> float:
        return sum(op.value for op in self._recurrent_operations) + sum(op.value for op in self._operations)

    def add_recurrent_operation(self, op: RecurrentOperation) -> None:
        if op in self._recurrent_operations:
            raise RecurrentOperationAlreadyExist(op.name)
        self._recurrent_operations.add(op)
        self._filter_operations()

    def update_recurrent_operation(self, op: RecurrentOperation) -> None:
        if op not in self._recurrent_operations:
            raise ValueError(f"Recurrent operation `{op.name}` does not exists")
        self._recurrent_operations.remove(op)
        self._recurrent_operations.add(op)
        self._filter_operations()

    @property
    def _recurrent_operation_names(self) -> set[str]:
        return {op.name for op in self._recurrent_operations}

    def _filter_operations(self) -> None:
        self._operations = {
            op for op in self._operations if all(not op.name.startswith(n) for n in self._recurrent_operation_names)
        }

    def remove_recurrent_operation(self, name: str) -> None:
        try:
            op = next(o for o in self._recurrent_operations if o.name == name)
        except StopIteration as err:
            raise RecurrentOperationNotFound(name) from err
        self._recurrent_operations.remove(op)

    def add_operation(self, op: Operation) -> None:
        self._operations.add(op)
        self._filter_operations()

    def update_operation(self, op: Operation) -> None:
        if op not in self._operations:
            raise ValueError(f"Operation `{op.id}` does not exists")
        self._operations.remove(op)
        self._operations.add(op)
        self._filter_operations()

    def remove_operation(self, op: Operation) -> None:
        if op not in self.operations:
            raise ValueError(f"Operation `{op.id}` does not exists")
        self._operations.remove(op)
