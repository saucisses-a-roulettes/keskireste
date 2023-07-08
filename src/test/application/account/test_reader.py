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

from src.application.account.creator import AccountCreationRequest, AccountCreator
from src.application.account.reader import AccountReader
from src.application.account.repository import AccountRepository, AccountNotFound
from src.domain.account import AccountId
from src.test.application.mock import MockIdFactory


def test_retrieve(
    account_creation_request: AccountCreationRequest,
    account_repository: AccountRepository,
    account_id_factory: MockIdFactory[AccountId],
):
    sample_account_creator = AccountCreator(repository=account_repository, id_factory=account_id_factory)
    account_reader = AccountReader(repository=account_repository)
    sample_account_creator.create(account_creation_request)

    assert account_reader.retrieve(account_id_factory.id_template)


def test_retrieve_not_found(
    account_repository: AccountRepository,
    account_id_factory: MockIdFactory[AccountId],
):
    account_reader = AccountReader(repository=account_repository)
    with pytest.raises(AccountNotFound):
        account_reader.retrieve(account_id_factory.id_template)
