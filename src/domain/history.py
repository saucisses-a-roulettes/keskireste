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


class RecurrentOperationAlreadyExist(ValueError):
    def __init__(self, name: str) -> None:
        super().__init__(f"Recurrent operation `{name}` already exists")


class RecurrentOperationNotFound(ValueError):
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


@dataclass
class SavingTransactionAspects(Generic[TSavingAccountId]):
    saving_account_id: TSavingAccountId


@dataclass
class LoanTransactionAspects:
    amount: float | None

    def __post_init__(self) -> None:
        if self.amount is not None and self.amount <= 0:
            raise ValueError("Amount must be greater than 0")


class Operation(Generic[TSavingAccountId]):
    def __init__(
        self,
        id_: str,
        day: int,
        name: str,
        amount: float,
        transaction_aspects: SavingTransactionAspects | LoanTransactionAspects | None = None,
    ) -> None:
        self._id = id_
        self._day = day
        self._name = name
        self._amount = amount
        self._transaction_aspects = transaction_aspects
        self._validate_data()

    def _validate_data(self) -> None:
        if self.day < 0 or self.day > 31:
            raise ValueError(f"Day `{self.day}` is invalid")
        if 128 < len(self.name) < 1:
            raise ValueError(f"Name size `{len(self.name)}` is invalid")

    @property
    def id(self) -> str:
        return self._id

    @property
    def day(self) -> int:
        return self._day

    @property
    def name(self) -> str:
        return self._name

    @property
    def amount(self) -> float:
        return self._amount

    @property
    def transaction_aspects(self) -> SavingTransactionAspects | LoanTransactionAspects | None:
        return self._transaction_aspects

    def __hash__(self):
        return hash(self.id)

    def __eq__(self, other: object) -> bool:
        return other.id == self.id if isinstance(other, Operation) else False

    def rename(self, name: str) -> None:
        self._name = name

    def modify_amount(self, amount: float) -> None:
        self._amount = amount

    def categorize_as_saving_account_transaction(self, transaction_aspects: SavingTransactionAspects) -> None:
        self._transaction_aspects = transaction_aspects

    def uncategorize_transaction(self) -> None:
        self._transaction_aspects = None

    def categorize_as_loan_transaction(self, transaction_aspects: LoanTransactionAspects) -> None:
        self._transaction_aspects = transaction_aspects


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


class OperationNotFound(ValueError):
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
        return sum(op.value for op in self._recurrent_operations) + sum(op.amount for op in self._operations)

    @property
    def saving_balance(self) -> float:
        return sum(op.amount for op in self._operations if type(op.transaction_aspects) == SavingTransactionAspects)

    @property
    def loan_balance(self) -> float:
        return sum(
            (op.transaction_aspects.amount * (op.amount / op.amount))
            if op.transaction_aspects.amount is not None
            else op.amount
            for op in self._operations
            if type(op.transaction_aspects) == LoanTransactionAspects
        )

    def add_recurrent_operation(self, op: RecurrentOperation) -> None:
        if op in self._recurrent_operations:
            raise RecurrentOperationAlreadyExist(op.name)
        self._recurrent_operations.add(op)

    def update_recurrent_operation(self, op: RecurrentOperation) -> None:
        if op not in self._recurrent_operations:
            raise ValueError(f"Recurrent operation `{op.name}` does not exists")
        self._recurrent_operations.remove(op)
        self._recurrent_operations.add(op)

    @property
    def _recurrent_operation_names(self) -> set[str]:
        return {op.name for op in self._recurrent_operations}

    def remove_recurrent_operation(self, name: str) -> None:
        try:
            op = next(o for o in self._recurrent_operations if o.name == name)
        except StopIteration as err:
            raise RecurrentOperationNotFound(name) from err
        self._recurrent_operations.remove(op)

    def add_operation(self, op: Operation) -> None:
        self._operations.add(op)

    def remove_operation(self, operation_id: str) -> None:
        operation = self._retrieve_operation(operation_id)
        self._operations = {op for op in self._operations if op.id != operation.id}

    def _retrieve_operation(self, operation_id: str) -> Operation:
        try:
            return next(op for op in self._operations if op.id == operation_id)
        except StopIteration as e:
            raise OperationNotFound(operation_id) from e

    def categorize_operation_as_saving_account_transaction(
        self, operation_id: str, transaction_aspects: SavingTransactionAspects
    ) -> None:
        operation = self._retrieve_operation(operation_id)
        operation.categorize_as_saving_account_transaction(transaction_aspects)

    def uncategorize_operation_as_saving_account_transaction(self, operation_id: str) -> None:
        operation = self._retrieve_operation(operation_id)
        operation.uncategorize_transaction()

    def categorize_operation_as_loan_transaction(
        self, operation_id: str, transaction_aspects: LoanTransactionAspects
    ) -> None:
        operation = self._retrieve_operation(operation_id)
        operation.categorize_as_loan_transaction(transaction_aspects)

    def rename_operation(self, operation_id: str, name: str) -> None:
        operation = self._retrieve_operation(operation_id)
        operation.rename(name)

    def modify_operation_amount(self, operation_id: str, amount: float) -> None:
        operation = self._retrieve_operation(operation_id)
        operation.modify_amount(amount)
