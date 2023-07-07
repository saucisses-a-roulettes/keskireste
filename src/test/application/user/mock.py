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

import ppa

from src.application.user.repository import UserRepository
from src.domain.user import UserId
from src.infrastructure.user.password.vault import UserPasswordVault, InvalidPassword
from src.test.application.mock import mock_id_factory, MockIdFactory
from src.test.domain.mocks import MockUserId
from src.shared.application.repository import EntityAlreadyExists, EntityNotFound
from src.shared.domain.email import EmailAddress


@ppa.in_memory_repository(
    entity_already_exists_exception=EntityAlreadyExists, entity_not_found_exception=EntityNotFound
)
class UserMockRepository(UserRepository):
    pass


@mock_id_factory(MockUserId)
class MockUserIdFactory(MockIdFactory[UserId]):
    pass


class UserPasswordVaultMock(UserPasswordVault):
    def __init__(self) -> None:
        self._passwords: dict[EmailAddress, str] = {}

    def save(self, email_address: EmailAddress, password: str) -> None:
        self._passwords[email_address] = password

    def check(self, email_address: EmailAddress, password: str) -> None:
        if self._passwords.get(email_address) != password:
            raise InvalidPassword()
