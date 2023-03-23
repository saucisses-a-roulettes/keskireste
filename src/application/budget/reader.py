from dataclasses import dataclass
from src.application.budget.repository import BudgetRepository
from src.domain.entity import Id


@dataclass(frozen=True)
class BudgetResponse:
    id_: Id
    histories_ids: frozenset[Id]


class BudgetReader:
    def __init__(self, repository: BudgetRepository) -> None:
        self._repository = repository

    def read(self, id_: Id) -> BudgetResponse:
        budget = self._repository.retrieve(id_)

        return BudgetResponse(id_=budget.id, histories_ids=budget.histories_ids)
