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
from typing import Generic

from src.application.exception import BadRequestException
from src.application.repository import CannotRetrieveEntity
from src.application.user.repository import UserRepository
from src.domain.user import TUserId, User


@dataclass(frozen=True)
class UserResponse:
    id: TUserId
    email: str


class UserReader(Generic[TUserId]):
    def __init__(self, repository: UserRepository) -> None:
        self._repository = repository

    def retrieve(self, user_id: TUserId) -> UserResponse:
        try:
            user: User = self._repository.retrieve(user_id)
        except CannotRetrieveEntity as err:
            raise BadRequestException(str(err)) from err

        return UserResponse(id=user.id, email=user.email)
