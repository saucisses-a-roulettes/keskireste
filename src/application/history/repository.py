from abc import ABC, abstractmethod
from src.domain.history import History


class HistoryRepository(ABC):
    @abstractmethod
    def retrieve(self, path: str) -> History:
        pass

    @abstractmethod
    def save(self, history: History) -> None:
        pass
