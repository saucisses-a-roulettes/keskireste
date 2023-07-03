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
from dependency_injector.wiring import inject, Provide
from fastapi import APIRouter, Depends
from pydantic import BaseModel, validator

from src.account.application.account.creator import AccountCreationRequest, AccountCreator
from src.account.domain.account import AccountName
from src.account.infrastructure.containers.in_memory import InMemoryContainer
from src.account.infrastructure.user.id import UserUUID

router = APIRouter()


class AccountCreationBody(BaseModel):
    user_id: str
    name: str
    reference_balance: float

    @validator("user_id")
    def validate_user_id(cls, user_id: str) -> str:
        UserUUID(user_id)
        return user_id

    @validator("name")
    def validate_name(cls, name: str) -> str:
        AccountName(name)
        return name


@router.post("/creation", status_code=201)
@inject
def create_account(
    body: AccountCreationBody, account_creator: AccountCreator = Depends(Provide[InMemoryContainer.account_creator])
) -> dict:
    account_creator.create(
        AccountCreationRequest(UserUUID(body.user_id), AccountName(body.name), body.reference_balance)
    )
    return {}
