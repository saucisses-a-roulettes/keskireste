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

from src.account.application.account.creator import AccountCreationRequest, AccountCreator
from src.account.application.account.repository import AccountRepository, AccountAlreadyExists
from src.account.test.domain.mocks import MockAccountId


def test_create_account(account_creation_request: AccountCreationRequest, account_repository: AccountRepository):
    sample_account_creator = AccountCreator(repository=account_repository)

    sample_account_creator.create(account_creation_request)

    assert account_repository.retrieve(MockAccountId("1"))


def test_create_account_already_exists(
    account_creation_request: AccountCreationRequest, account_repository: AccountRepository
):
    sample_account_creator = AccountCreator(repository=account_repository)
    sample_account_creator.create(account_creation_request)

    with pytest.raises(AccountAlreadyExists):
        sample_account_creator.create(account_creation_request)
