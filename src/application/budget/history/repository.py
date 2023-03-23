from abc import ABC, abstractmethod
from src.domain.entity import Id
from src.domain.history import History


class HistoryRepository(ABC):
    @abstractmethod
    def retrieve(self, id_: Id) -> History:
        pass

    @abstractmethod
    def create(self, history: History) -> None:
        pass

    @abstractmethod
    def update(self, history: History) -> None:
        pass
