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
import datetime

from dependency_injector.wiring import inject, Provide
from fastapi import APIRouter, Depends
from pydantic import BaseModel, validator

from src.application.transaction.creator import TransactionCreationRequest
from src.domain.account import AccountId
from src.infrastructure.account.id import AccountUUID
from src.infrastructure.containers.in_memory import InMemoryContainer

router = APIRouter()


class TransactionCreationBody(BaseModel):
    account_id: str
    date: datetime.date
    label: str
    amount: float

    @validator("account_id")
    def validate_account_id(cls, account_id: str) -> str:
        AccountUUID(account_id)
        return account_id


@router.post("/creation", status_code=201)
@inject
def create_transaction(
    body: TransactionCreationBody, transaction_creator=Depends(Provide[InMemoryContainer.transaction_creator])
) -> dict:
    transaction_creator.create(
        TransactionCreationRequest(AccountUUID(body.account_id), body.date, body.label, body.amount)
    )
    return {}
