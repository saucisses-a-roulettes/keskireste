from abc import ABC, abstractmethod

from src.domain.transaction import Transaction, TransactionId
from src.shared.application.repository import EntityAlreadyExists, EntityNotFound


class TransactionAlreadyExists(EntityAlreadyExists):
    def __init__(self, transaction_id: TransactionId) -> None:
        super().__init__(f"Transaction `{transaction_id}` already exists")
        self._transaction_id = transaction_id

    @property
    def transaction_id(self) -> TransactionId:
        return self._transaction_id


class TransactionNotFound(EntityNotFound):
    def __init__(self, transaction_id: TransactionId) -> None:
        super().__init__(f"Transaction `{transaction_id}` not found")
        self._transaction_id = transaction_id

    @property
    def transaction_id(self) -> TransactionId:
        return self._transaction_id


class TransactionRepository(ABC):
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
