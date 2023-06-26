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

from src.account.application.account.creator import AccountCreationRequest
from src.account.application.account.deleter import AccountDeletionRequest
from src.account.domain.account import AccountName
from src.account.test.application.account.mock import AccountMockRepository
from src.account.test.domain.mocks import MockAccountId, MockUserId


@pytest.fixture
def account_repository():
    return AccountMockRepository()


@pytest.fixture
def account_creation_request():
    return AccountCreationRequest(
        id=MockAccountId("1"), user_id=MockUserId("1"), name=AccountName("account_name"), reference_balance=100.0
    )


@pytest.fixture
def account_deletion_request():
    return AccountDeletionRequest(id=MockAccountId("1"))
