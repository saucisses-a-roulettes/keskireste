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
import pytest

from src.application.reccurring_transaction.creator import (
    RecurringTransactionCreationRequest,
    RecurringTransactionCreator,
)
from src.application.reccurring_transaction.repository import (
    RecurringTransactionRepository,
    RecurringTransactionAlreadyExists,
)
from src.test.domain.mocks import RecurringTransactionMockId


def test_create_recurring_transaction(
    recurring_transaction_creation_request: RecurringTransactionCreationRequest,
    recurring_transaction_repository: RecurringTransactionRepository,
):
    sample_recurring_transaction_creator = RecurringTransactionCreator(repository=recurring_transaction_repository)

    sample_recurring_transaction_creator.create(recurring_transaction_creation_request)

    assert recurring_transaction_repository.retrieve(RecurringTransactionMockId("1"))


def test_create_recurring_transaction_already_exists(
    recurring_transaction_creation_request: RecurringTransactionCreationRequest,
    recurring_transaction_repository: RecurringTransactionRepository,
):
    sample_recurring_transaction_creator = RecurringTransactionCreator(repository=recurring_transaction_repository)
    sample_recurring_transaction_creator.create(recurring_transaction_creation_request)

    with pytest.raises(RecurringTransactionAlreadyExists):
        sample_recurring_transaction_creator.create(recurring_transaction_creation_request)
