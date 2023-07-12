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
from pydantic import BaseModel

from src.application.transaction.updater import TransactionUpdater, TransactionUpdateRequest
from src.infrastructure.account.id import AccountUUID
from src.infrastructure.containers.in_memory import InMemoryContainer
from src.infrastructure.transaction.id import TransactionUUID

router = APIRouter()


class TransactionUpdateBody(BaseModel):
    date: datetime.date
    label: str
    amount: float


@router.put("/transaction/{transaction_id}", status_code=200)
@inject
def update_transaction(
    transaction_id: str,
    body: TransactionUpdateBody,
    transaction_updater: TransactionUpdater = Depends(Provide[InMemoryContainer.transaction_updater]),
) -> None:
    transaction_updater.update(
        TransactionUpdateRequest(TransactionUUID(transaction_id), body.date, body.label, body.amount)
    )
