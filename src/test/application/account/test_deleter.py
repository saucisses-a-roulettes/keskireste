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
from pytest_mock import MockFixture

from src.application.account.creator import AccountCreator, AccountCreationRequest
from src.application.account.deleter import AccountDeletionRequest, AccountDeleter
from src.application.account.repository import AccountRepository, AccountNotFound
from src.test.application.account.mock import MockAccountIdFactory


def test_delete_account(
    mocker: MockFixture,
    account_creation_request: AccountCreationRequest,
    account_deletion_request: AccountDeletionRequest,
    account_repository: AccountRepository,
    account_id_factory: MockAccountIdFactory,
):
    spy = mocker.spy(account_repository, "delete")
    sample_account_creator = AccountCreator(repository=account_repository, id_factory=account_id_factory)
    sample_account_deleter = AccountDeleter(repository=account_repository)
    sample_account_creator.create(account_creation_request)

    sample_account_deleter.delete(account_deletion_request)

    spy.assert_called_once_with(account_deletion_request.id)


def test_delete_unexisting_account(
    account_deletion_request: AccountDeletionRequest, account_repository: AccountRepository
):
    sample_account_deleter = AccountDeleter(repository=account_repository)

    with pytest.raises(AccountNotFound):
        sample_account_deleter.delete(account_deletion_request)
