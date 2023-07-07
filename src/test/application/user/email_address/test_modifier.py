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
from src.application.user.creator import UserCreator, UserCreationRequest
from src.application.user.email_address.modifier import UserEmailAddressModificationRequest, UserEmailAddressModifier
from src.application.user.repository import UserRepository
from src.domain.user import UserId
from src.shared.domain.email import EmailAddress
from src.test.application.mock import MockIdFactory


def test_modify(
    user_creation_request: UserCreationRequest,
    user_repository: UserRepository,
    user_id_factory: MockIdFactory[UserId],
):
    user_email_address_modifier = UserEmailAddressModifier(repository=user_repository)
    sample_user_creator = UserCreator(repository=user_repository, id_factory=user_id_factory)
    sample_user_creator.create(user_creation_request)

    new_email_address = EmailAddress("new_email_address@mock.com")

    user_email_address_modifier.modify(
        UserEmailAddressModificationRequest(user_id=user_id_factory.id_template, email_address=new_email_address)
    )

    assert user_repository.retrieve(user_id_factory.id_template).email_address == new_email_address
