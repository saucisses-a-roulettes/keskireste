from src.application.budget.repository import BudgetRepository
from src.domain.entity import Id
from src.domain.budget import Budget


class BudgetCreator:
    def __init__(self, repository: BudgetRepository) -> None:
        self._repository = repository

    def create(self, id_: Id) -> None:
        self._repository.create(Budget(id_=id_, histories_ids=frozenset()))
