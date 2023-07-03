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
from dependency_injector.containers import DeclarativeContainer
from dependency_injector.providers import Factory

from src.account.application.account.creator import AccountCreator
from src.account.test.application.account.mock import AccountMockRepository, MockAccountIdFactory
from src.account.test.application.recurring_transaction.mock import RecurringTransactionMockRepository
from src.account.test.application.transaction.mock import TransactionMockRepository
from src.account.test.application.user.mock import UserMockRepository


class InMemoryContainer(DeclarativeContainer):
    user_repository = Factory(UserMockRepository)
    account_repository = Factory(AccountMockRepository)
    transaction_repository = Factory(TransactionMockRepository)
    recurring_transaction_repository = Factory(RecurringTransactionMockRepository)

    account_id_factory = Factory(MockAccountIdFactory)

    account_creator = Factory(AccountCreator, repository=account_repository, id_factory=account_id_factory)
