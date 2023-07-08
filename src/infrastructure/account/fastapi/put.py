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
from fastapi import APIRouter, Depends
from pydantic import BaseModel

from src.application.account.updater import AccountUpdater, AccountUpdateRequest
from src.domain.account import AccountName
from src.infrastructure.account.id import AccountUUID
from src.infrastructure.containers.in_memory import InMemoryContainer

router = APIRouter()


class AccountUpdateBody(BaseModel):
    name: str
    reference_balance: float


@router.put("/account/{account_id}", status_code=200)
@inject
def update_account(
    account_id: str,
    body: AccountUpdateBody,
    account_updater: AccountUpdater = Depends(Provide[InMemoryContainer.account_updater]),
) -> None:
    account_updater.update(
        AccountUpdateRequest(AccountUUID(account_id), AccountName(body.name), body.reference_balance)
    )
