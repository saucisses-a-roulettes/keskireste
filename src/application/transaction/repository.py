from abc import ABC, abstractmethod
from typing import Generic

from src.domain.transaction import Transaction, TransactionId
from src.shared.application.repository import EntityAlreadyExists, EntityNotFound
from src.shared.domain.entity import TId


class TransactionAlreadyExists(EntityAlreadyExists, Generic[TId]):
    def __init__(self, transaction_id: TId) -> None:
        super().__init__(f"Transaction `{transaction_id}` already exists")
        self._transaction_id = transaction_id

    @property
    def transaction_id(self) -> TId:
        return self._transaction_id


class TransactionNotFound(EntityNotFound, Generic[TId]):
    def __init__(self, transaction_id: TId) -> None:
        super().__init__(f"Transaction `{transaction_id}` not found")
        self._transaction_id = transaction_id

    @property
    def transaction_id(self) -> TId:
        return self._transaction_id


class TransactionRepository(ABC, Generic[TId]):
    @abstractmethod
    def add(self, transaction: Transaction) -> None:
        """
        :param transaction:
        :raises EntityAlreadyExists
        """
        pass

    @abstractmethod
    def retrieve(self, id_: TransactionId) -> Transaction:
        """
        :param id_:
        :raises EntityNotFound
        """
        pass

    @abstractmethod
    def delete(self, id_: TransactionId) -> None:
        """
        :param id_:
        :raises EntityNotFound
        """

    @abstractmethod
    def update(self, transaction: Transaction) -> None:
        """
        :param transaction:
        :raises EntityNotFound
        """
