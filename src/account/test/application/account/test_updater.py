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
from pytest_mock import MockerFixture

from src.account.application.account.creator import AccountCreationRequest, AccountCreator
from src.account.application.account.repository import AccountRepository, AccountNotFound
from src.account.application.account.updater import AccountUpdateRequest, AccountUpdater
from src.account.domain.account import AccountName
from src.account.test.domain.mocks import MockAccountId


@pytest.fixture
def account_update_request(account_creation_request: AccountUpdateRequest):
    return AccountUpdateRequest(
        id=account_creation_request.id,
        name=AccountName(f"{account_creation_request.name}_updated"),
        reference_balance=account_creation_request.reference_balance + 10,
    )


def test_update_account(
    mocker: MockerFixture,
    account_creation_request: AccountCreationRequest,
    account_update_request: AccountUpdateRequest,
    account_repository: AccountRepository,
):
    spy = mocker.spy(account_repository, "update")
    sample_account_creator = AccountCreator(repository=account_repository)
    sample_account_updater = AccountUpdater(repository=account_repository)
    sample_account_creator.create(account_creation_request)

    account = account_repository.retrieve(MockAccountId("1"))

    account.rename(account_update_request.name)
    account.modify_reference_balance(account_update_request.reference_balance)

    sample_account_updater.update(account_update_request)

    spy.assert_called_once_with(account)


def test_update_unexisting_account(account_update_request: AccountUpdateRequest, account_repository: AccountRepository):
    sample_account_updater = AccountUpdater(repository=account_repository)

    with pytest.raises(AccountNotFound):
        sample_account_updater.update(account_update_request)
