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

from src.shared.domain.email import EmailAddress
from src.shared.test.domain.mock import MockId
from src.user.application.creator import UserCreationRequest, UserCreator
from src.user.application.repository import UserAlreadyExists, UserRepository
from src.user.domain.user import UserName
from src.user.test.application.mock import UserMockRepository


@pytest.fixture
def user_creation_request():
    return UserCreationRequest(id=MockId("1"), email=EmailAddress("john@example.com"), username=UserName("john_doe"))


@pytest.fixture
def user_repository():
    return UserMockRepository()


def test_create_user(user_creation_request: UserCreationRequest, user_repository: UserRepository):
    sample_user_creator = UserCreator(repository=user_repository)

    sample_user_creator.create(user_creation_request)

    assert user_repository.retrieve(MockId("1"))


def test_create_user_already_exists(user_creation_request: UserCreationRequest, user_repository: UserRepository):
    sample_user_creator = UserCreator(repository=user_repository)
    sample_user_creator.create(user_creation_request)

    with pytest.raises(UserAlreadyExists):
        sample_user_creator.create(user_creation_request)
