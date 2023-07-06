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
from src.account.domain.user import UserId
from src.account.test.application.mock import MockIdFactory


def test_create_user(
    user_creation_request: UserCreationRequest,
    user_repository: UserRepository,
    user_id_factory: MockIdFactory[UserId],
):
    sample_user_creator = UserCreator(repository=user_repository, id_factory=user_id_factory)

    sample_user_creator.create(user_creation_request)

    assert user_repository.retrieve(user_id_factory.id_template)


def test_create_user_already_exists(
    user_creation_request: UserCreationRequest,
    user_repository: UserRepository,
    user_id_factory: MockIdFactory[UserId],
):
    sample_user_creator = UserCreator(repository=user_repository, id_factory=user_id_factory)
    sample_user_creator.create(user_creation_request)

    with pytest.raises(UserAlreadyExists):
        sample_user_creator.create(user_creation_request)
