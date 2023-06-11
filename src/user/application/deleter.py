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

from src.shared.application.repository import EntityNotFound
from src.shared.domain.entity import TId
from src.user.application.repository import UserRepository, UserNotFound


@dataclass(frozen=True)
class UserDeletionRequest(Generic[TId]):
    id: TId


class UserDeleter:
    def __init__(self, repository: UserRepository) -> None:
        self._repository = repository

    def delete(self, request: UserDeletionRequest) -> None:
        try:
            self._repository.delete(request.id)
        except EntityNotFound as e:
            raise UserNotFound(user_id=request.id) from e
