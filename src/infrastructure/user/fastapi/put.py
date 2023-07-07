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
from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter
from fastapi import Depends
from pydantic import BaseModel

from src.application.user.updater import UserUpdater, UserUpdateRequest
from src.domain.user import UserName
from src.infrastructure.containers.in_memory import InMemoryContainer
from src.infrastructure.user.id import UserUUID

router = APIRouter()


class UserUpdateBody(BaseModel):
    username: str


@router.put("/{user_id}", status_code=200)
@inject
async def update_user(
    user_id: str, body: UserUpdateBody, user_updater: UserUpdater = Depends(Provide[InMemoryContainer.user_updater])
) -> None:
    user_update_request = UserUpdateRequest(id=UserUUID(user_id), username=UserName(body.username))

    user_updater.update(user_update_request)
