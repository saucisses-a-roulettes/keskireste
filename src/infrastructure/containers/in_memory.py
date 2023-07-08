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

from src.application.account.creator import AccountCreator
from src.application.account.deleter import AccountDeleter
from src.application.account.updater import AccountUpdater
from src.application.user.creator import UserCreator
from src.application.user.deleter import UserDeleter
from src.application.user.email_address.modifier import UserEmailAddressModifier
from src.application.user.reader import UserReader
from src.application.user.subscription.email_address.validator import EmailAddressValidator
from src.application.user.updater import UserUpdater
from src.test.application.account.mock import AccountMockRepository, MockAccountIdFactory
from src.test.application.recurring_transaction.mock import RecurringTransactionMockRepository
from src.test.application.transaction.mock import TransactionMockRepository
from src.test.application.user.email_address.mock import ValidationEmailMockSender, EmailAddressCheckerMock
from src.test.application.user.mock import UserMockRepository, MockUserIdFactory, UserPasswordVaultMock


class InMemoryContainer(DeclarativeContainer):
    user_repository = Factory(UserMockRepository)
    user_id_factory = Factory(MockUserIdFactory)
    user_creator = Factory(UserCreator, repository=user_repository, id_factory=user_id_factory)
    user_updater = Factory(UserUpdater, repository=user_repository)
    user_deleter = Factory(UserDeleter, repository=user_repository)
    user_reader = Factory(UserReader, repository=user_repository)
    user_password_vault = Factory(UserPasswordVaultMock)
    user_email_address_modifier = Factory(UserEmailAddressModifier, repository=user_repository)

    account_repository = Factory(AccountMockRepository)
    account_id_factory = Factory(MockAccountIdFactory)
    account_creator = Factory(AccountCreator, repository=account_repository, id_factory=account_id_factory)
    account_updater = Factory(AccountUpdater, repository=account_repository)
    account_deleter = Factory(AccountDeleter, repository=account_repository)

    transaction_repository = Factory(TransactionMockRepository)
    recurring_transaction_repository = Factory(RecurringTransactionMockRepository)

    email_address_checker = Factory(EmailAddressCheckerMock)
    validation_email_sender = Factory(ValidationEmailMockSender)
    email_address_validator = Factory(
        EmailAddressValidator,
        email_address_checker=email_address_checker,
        validation_email_sender=validation_email_sender,
    )
