from abc import ABC, abstractmethod
from typing import Generic
from src.domain.entity import TId
from src.domain.history import History


class HistoryRepository(ABC, Generic[TId]):
    @abstractmethod
    def retrieve(self, id_: TId) -> History[TId]:
        pass

    @abstractmethod
    def create(self, history: History[TId]) -> None:
        pass

    @abstractmethod
    def update(self, history: History[TId]) -> None:
        pass
