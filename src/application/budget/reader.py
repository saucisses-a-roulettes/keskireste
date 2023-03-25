from dataclasses import dataclass
from typing import Generic
from src.application.budget.repository import BudgetRepository
from src.domain.entity import Id, TId


@dataclass(frozen=True)
class BudgetResponse(Generic[TId]):
    id: Id
    histories_ids: frozenset[TId]


class BudgetReader(Generic[TId]):
    def __init__(self, repository: BudgetRepository) -> None:
        self._repository = repository

    def retrieve(self, id_: TId) -> BudgetResponse[TId]:
        budget = self._repository.retrieve(id_)

        return BudgetResponse(id=budget.id, histories_ids=budget.histories_ids)
