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

from src.shared.domain.email import EmailAddress
from src.user.application.creator import UserCreationRequest, UserCreator
from src.user.application.repository import UserRepository, UserNotFound
from src.user.application.updater import UserUpdateRequest, UserUpdater
from src.user.domain.user import UserName
from src.user.test.domain.mocks import MockUserId


@pytest.fixture
def user_update_request(user_creation_request: UserCreationRequest):
    return UserUpdateRequest(
        id=user_creation_request.id,
        email=EmailAddress(str(user_creation_request.email).replace("john", "john_updated")),
        username=UserName(f"{user_creation_request.username}_updated"),
    )


def test_update_user(
    mocker: MockerFixture,
    user_creation_request: UserCreationRequest,
    user_update_request: UserUpdateRequest,
    user_repository: UserRepository,
):
    spy = mocker.spy(user_repository, "update")
    sample_user_creator = UserCreator(repository=user_repository)
    sample_user_updater = UserUpdater(repository=user_repository)
    sample_user_creator.create(user_creation_request)

    user = user_repository.retrieve(MockUserId("1"))

    user.rename(user_update_request.username)
    user.change_email(user_update_request.email)

    sample_user_updater.update(user_update_request)

    spy.assert_called_once_with(user)


def test_update_unexisting_user(user_update_request: UserUpdateRequest, user_repository: UserRepository):
    sample_user_updater = UserUpdater(repository=user_repository)

    with pytest.raises(UserNotFound):
        sample_user_updater.update(user_update_request)
