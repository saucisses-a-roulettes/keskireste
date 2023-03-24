from abc import ABC, abstractmethod
from typing import TypeVar


class Id(ABC):
    @abstractmethod
    def __str__(self) -> str:
        pass

    @abstractmethod
    def __hash__(self):
        pass


TId = TypeVar("TId", bound=Id)
