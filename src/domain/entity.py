from abc import ABC, abstractmethod
from typing import Self


class Id(ABC):
    @classmethod
    @abstractmethod
    def from_string(cls, s: str) -> Self:
        pass

    @abstractmethod
    def __str__(self) -> str:
        pass

    @abstractmethod
    def __hash__(self):
        pass
