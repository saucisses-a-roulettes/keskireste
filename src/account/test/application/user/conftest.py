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

from src.account.application.user.creator import UserCreationRequest
from src.account.application.user.repository import UserRepository
from src.account.domain.user import UserName, UserId
from src.account.infrastructure.containers.in_memory import InMemoryContainer
from src.account.test.application.mock import MockIdFactory
from src.shared.domain.email import EmailAddress


@pytest.fixture
def user_repository(container: InMemoryContainer) -> UserRepository:
    return container.user_repository()


@pytest.fixture
def user_id_factory(container: InMemoryContainer) -> MockIdFactory[UserId]:
    return container.user_id_factory()


@pytest.fixture
def user_creation_request(user_id_factory: MockIdFactory[UserId]) -> UserCreationRequest:
    return UserCreationRequest(email_address=EmailAddress("john@example.com"), username=UserName("john_doe"))
