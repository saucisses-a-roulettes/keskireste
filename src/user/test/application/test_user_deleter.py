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

from src.user.application.creator import UserCreationRequest, UserCreator
from src.user.application.deleter import UserDeletionRequest, UserDeleter
from src.user.application.repository import UserRepository, UserNotFound


@pytest.fixture
def user_deletion_request(user_creation_request: UserCreationRequest):
    return UserDeletionRequest(id=user_creation_request.id)


def test_delete_user(
    mocker: MockerFixture,
    user_creation_request: UserCreationRequest,
    user_deletion_request: UserDeletionRequest,
    user_repository: UserRepository,
):
    spy = mocker.spy(user_repository, "delete")
    sample_user_creator = UserCreator(repository=user_repository)
    sample_user_deleter = UserDeleter(repository=user_repository)
    sample_user_creator.create(user_creation_request)

    sample_user_deleter.delete(user_deletion_request)

    spy.assert_called_once_with(user_deletion_request.id)


def test_delete_unexisting_user(user_deletion_request: UserDeletionRequest, user_repository: UserRepository):
    sample_user_deleter = UserDeleter(repository=user_repository)

    with pytest.raises(UserNotFound):
        sample_user_deleter.delete(user_deletion_request)
