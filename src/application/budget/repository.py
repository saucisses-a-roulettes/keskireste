from abc import ABC, abstractmethod
from src.domain.budget import Budget
from src.domain.entity import Id


class BudgetRepository(ABC):
    @abstractmethod
    def retrieve(self, id_: Id) -> Budget:
        pass

    @abstractmethod
    def create(self, budget: Budget) -> None:
        pass
