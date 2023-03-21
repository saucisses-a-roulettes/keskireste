import datetime
import pathlib
from dataclasses import Field, dataclass, field


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
    year: int = field(hash=True)
    month: int = field(hash=True)
    name: str = field(hash=True)
    value: float = field(hash=False)


@dataclass(frozen=True)
class Operation:
    date: datetime.datetime
    name: str
    value: float


class History:
    def __init__(
        self,
        path: str,
        recurrent_incomes: set[RecurrentOperation],
        recurrent_expenses: set[RecurrentOperation],
        operations: set[Operation],
        filtered_operations: set[str],
    ) -> None:
        self._path = str(Path(path))
        self._monthly_incomes = recurrent_incomes
        self._monthly_expenses = recurrent_expenses
        self._operations = operations
        self._filtered_operations = filtered_operations

    @property
    def path(self) -> str:
        return self._path

    @property
    def recurrent_incomes(self) -> set[RecurrentOperation]:
        return self._monthly_incomes

    @property
    def recurrent_expenses(self) -> set[RecurrentOperation]:
        return self._monthly_expenses

    @property
    def operations(self) -> set[Operation]:
        return self._operations

    def _update_filtered_operations(self) -> None:
        self._filtered_operations = {ri.name for ri in self._monthly_incomes} | {
            re.name for re in self._monthly_expenses
        }
        self._operations = {
            op for op in self._operations if not any(op.name.startswith(f) for f in self._filtered_operations)
        }

    def add_recurrent_operation(self, op: RecurrentOperation) -> None:
        if op.value > 0:
            self._monthly_incomes.add(op)
        elif op.value < 0:
            self._monthly_expenses.add(op)
        self._update_filtered_operations()

    def remove_recurrent_operation(self, op: RecurrentOperation) -> None:
        if op.value > 0:
            self._monthly_incomes.remove(op)
        elif op.value < 0:
            self._monthly_expenses.remove(op)
        self._update_filtered_operations()

    def add_operation(self, op: Operation) -> None:
        if all(not op.name.startswith(f) for f in self._filtered_operations):
            self._operations.add(op)

    @property
    def filtered_operations(self) -> set[str]:
        return self._filtered_operations
