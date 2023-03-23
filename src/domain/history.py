import pathlib
from dataclasses import dataclass
from src.domain.entity import Id


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


class History:
    def __init__(
        self, id_: Id, date: Date, recurrent_operations: set[RecurrentOperation], operations: set[Operation]
    ) -> None:
        self._id = id_
        self._date = date
        self._recurrent_operations = recurrent_operations
        self._operations = operations

    def __hash__(self):
        return hash(self._id)

    @property
    def id(self) -> Id:
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
