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
from dataclasses import dataclass

from src.application.user.repository import UserRepository, UserAlreadyExists
from src.domain.user import UserName, User, UserId
from src.shared.application.id import IdFactory
from src.shared.application.repository import EntityAlreadyExists
from src.shared.domain.email import EmailAddress


@dataclass(frozen=True)
class UserCreationRequest:
    email_address: EmailAddress
    username: UserName


class UserCreator:
    def __init__(self, repository: UserRepository, id_factory: IdFactory[UserId]) -> None:
        self._id_factory = id_factory
        self._repository = repository

    def create(self, request: UserCreationRequest) -> None:
        user = User(id_=self._id_factory.generate_id(), email_address=request.email_address, username=request.username)

        try:
            self._repository.add(user)
        except EntityAlreadyExists as e:
            raise UserAlreadyExists(user_id=user.id) from e
