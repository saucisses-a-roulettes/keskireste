#  /*
#   * Copyright (c) 2023 Gael Monachon
#   *
#   * This program is free software: you can redistribute it and/or modify
#   * it under the terms of the GNU General Public License as published by
#   * the Free Software Foundation, either version 3 of the License, or
#   * (at your option) any later version.
#   *
#   * This program is distributed in the hope that it will be useful,
#   * but WITHOUT ANY WARRANTY; without even the implied warranty of
#   * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   * GNU General Public License for more details.
#   *
#   * You should have received a copy of the GNU General Public License
#   * along with this program.  If not, see <https://www.gnu.org/licenses/>.
#   */
from abc import ABC, abstractmethod
from typing import Generic

from src.domain.recurring_transaction import RecurringTransaction, RecurringTransactionId
from src.shared.application.repository import EntityAlreadyExists, EntityNotFound


class RecurringTransactionAlreadyExists(EntityAlreadyExists):
    def __init__(self, recurring_transaction_id: RecurringTransactionId) -> None:
        super().__init__(f"Recurring Transaction `{recurring_transaction_id}` already exists")
        self._recurring_transaction_id = recurring_transaction_id

    @property
    def recurring_transaction_id(self) -> RecurringTransactionId:
        return self._recurring_transaction_id


class RecurringTransactionNotFound(EntityNotFound):
    def __init__(self, recurring_transaction_id: RecurringTransactionId) -> None:
        super().__init__(f"Recurring Transaction `{recurring_transaction_id}` not found")
        self._recurring_transaction_id = recurring_transaction_id

    @property
    def recurring_transaction_id(self) -> RecurringTransactionId:
        return self._recurring_transaction_id


class RecurringTransactionRepository(ABC):
    @abstractmethod
    def add(self, recurring_transaction: RecurringTransaction) -> None:
        """
        :param :recurring_transaction:
        :raises EntityAlreadyExists
        """
        pass

    @abstractmethod
    def retrieve(self, id_: RecurringTransactionId) -> RecurringTransaction:
        """
        :param id_:
        :raises EntityNotFound
        """
        pass

    @abstractmethod
    def delete(self, id_: RecurringTransactionId) -> None:
        """
        :param id_:
        :raises EntityNotFound
        """

    @abstractmethod
    def update(self, recurring_transaction: RecurringTransaction) -> None:
        """
        :param recurring_transaction:
        :raises EntityNotFound
        """
