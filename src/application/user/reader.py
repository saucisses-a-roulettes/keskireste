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

from src.application.user.repository import UserRepository, UserNotFound
from src.domain.user import UserName, UserId
from src.shared.application.repository import EntityNotFound
from src.shared.domain.email import EmailAddress


@dataclass(frozen=True)
class UserRetrievalResponse:
    id: UserId
    username: UserName
    email_address: EmailAddress


class UserReader:
    def __init__(self, repository: UserRepository) -> None:
        self._repository = repository

    def retrieve(self, user_id: UserId) -> UserRetrievalResponse:
        try:
            user = self._repository.retrieve(user_id)
        except EntityNotFound as e:
            raise UserNotFound(user_id=user_id) from e
        return UserRetrievalResponse(
            id=user.id,
            username=user.username,
            email_address=user.email_address,
        )
