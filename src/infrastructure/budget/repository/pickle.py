import pickle
from src.application.budget.repository import BudgetRepository
from src.domain.budget import Budget
from src.domain.entity import Id
from src.infrastructure.budget.repository.model import BudgetPickleModel


class BudgetPickleRepository(BudgetRepository):
    def retrieve(self, id_: Id) -> Budget:
        with open(str(id_), "rb") as f:
            model: BudgetPickleModel = pickle.load(f)
        return Budget(id_=id_, histories_ids=frozenset({h.id for h in model.histories}))

    def create(self, budget: Budget) -> None:
        model = BudgetPickleModel(histories=frozenset())
        with open(str(budget.id), "wb") as f:
            pickle.dump(model, f)
