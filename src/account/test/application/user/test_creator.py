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

from src.account.application.user.creator import UserCreationRequest, UserCreator
from src.account.application.user.repository import UserAlreadyExists, UserRepository
from src.account.test.domain.mocks import MockUserId


def test_create_user(user_creation_request: UserCreationRequest, user_repository: UserRepository):
    sample_user_creator = UserCreator(repository=user_repository)

    sample_user_creator.create(user_creation_request)

    assert user_repository.retrieve(MockUserId("1"))


def test_create_user_already_exists(user_creation_request: UserCreationRequest, user_repository: UserRepository):
    sample_user_creator = UserCreator(repository=user_repository)
    sample_user_creator.create(user_creation_request)

    with pytest.raises(UserAlreadyExists):
        sample_user_creator.create(user_creation_request)
