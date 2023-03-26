
from src.domain.entity import Id


class BudgetPath(Id):
    def __init__(self, value: str) -> None:
        self._value = value

    def __str__(self) -> str:
        return self._value

    def __hash__(self):
        return hash(self._value)


