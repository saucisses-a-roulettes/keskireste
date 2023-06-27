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

import datetime

import pytest

from src.account.application.transaction.creator import TransactionCreationRequest
from src.account.application.transaction.deleter import TransactionDeletionRequest
from src.account.infrastructure.containers.in_memory import InMemoryContainer
from src.account.test.domain.mocks import MockTransactionId, MockAccountId


@pytest.fixture
def transaction_repository(container: InMemoryContainer):
    return container.transaction_repository()


@pytest.fixture
def transaction_creation_request():
    return TransactionCreationRequest(
        id=MockTransactionId("1"), account_id=MockAccountId("1"), date=datetime.date.today(), label="label", amount=1.0
    )


@pytest.fixture
def transaction_deletion_request():
    return TransactionDeletionRequest(id=MockTransactionId("1"))
