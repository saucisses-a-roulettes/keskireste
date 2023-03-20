import datetime
import pathlib
from dataclasses import dataclass


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


@dataclass(frozen=True)
class Operation:
    date: datetime.datetime
    name: str
    value: float


class History:
    def __init__(
        self,
        path: str,
        monthly_incomes: set[RecurrentOperation],
        monthly_expenses: set[RecurrentOperation],
        operations: set[Operation],
        filtered_operations: set[str],
    ) -> None:
        self._path = str(Path(path))
        self._monthly_incomes = monthly_incomes
        self._monthly_expenses = monthly_expenses
        self._operations = operations
        self._filtered_operations = filtered_operations

    @property
    def path(self) -> str:
        return self._path

    @property
    def monthly_incomes(self) -> set[RecurrentOperation]:
        return self._monthly_incomes

    @property
    def monthly_expenses(self) -> set[RecurrentOperation]:
        return self._monthly_expenses

    @property
    def operations(self) -> set[Operation]:
        return self._operations

    def add_monthly_operation(self, op: RecurrentOperation) -> None:
        if op.value > 0:
            self._monthly_incomes.add(op)
        elif op.value < 0:
            self._monthly_expenses.add(op)

    @property
    def filtered_operations(self) -> set[str]:
        return self._filtered_operations

    def add_filtered_operation(self, name: str) -> None:
        self._filtered_operations.add(name)

    def add_operations(self, operations: set[Operation]) -> None:
        self._operations |= {o for o in operations if o.name not in self._filtered_operations}
