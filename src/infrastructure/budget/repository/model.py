from dataclasses import dataclass
from src.domain.history import History


@dataclass(frozen=True)
class BudgetPickleModel:
    histories: frozenset[History]
