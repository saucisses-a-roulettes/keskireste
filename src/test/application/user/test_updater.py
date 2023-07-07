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

from src.application.user.creator import UserCreationRequest, UserCreator
from src.application.user.repository import UserRepository, UserNotFound
from src.application.user.updater import UserUpdateRequest, UserUpdater
from src.domain.user import UserName, User, UserId
from src.test.application.mock import MockIdFactory
from src.shared.domain.email import EmailAddress


@pytest.fixture
def user_update_request(user_id_factory: MockIdFactory[UserId], user_creation_request: UserCreationRequest):
    return UserUpdateRequest(
        id=user_id_factory.generate_id(),
        email_address=EmailAddress(str(user_creation_request.email_address).replace("john", "john_updated")),
        username=UserName(f"{user_creation_request.username}_updated"),
    )


def test_update_user(
    user_creation_request: UserCreationRequest,
    user_update_request: UserUpdateRequest,
    user_repository: UserRepository,
    user_id_factory: MockIdFactory[UserId],
):
    sample_user_creator = UserCreator(repository=user_repository, id_factory=user_id_factory)
    sample_user_updater = UserUpdater(repository=user_repository)
    sample_user_creator.create(user_creation_request)

    user = user_repository.retrieve(user_id_factory.id_template)

    reference_user = User(user.id, user.email_address, user.username)

    reference_user.rename(user_update_request.username)
    reference_user.change_email_address(user_update_request.email_address)

    sample_user_updater.update(user_update_request)

    user = user_repository.retrieve(user.id)

    assert user.username == reference_user.username and user.email_address == reference_user.email_address


def test_update_unexisting_user(user_update_request: UserUpdateRequest, user_repository: UserRepository):
    sample_user_updater = UserUpdater(repository=user_repository)

    with pytest.raises(UserNotFound):
        sample_user_updater.update(user_update_request)
