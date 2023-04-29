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

from src.application.budget.history.repository import HistoryRepository
from src.application.exception import BadRequestException
from src.application.repository import CannotRetrieveEntity
from src.domain.budget.budget import TBudgetId
from src.domain.budget.history import (
    Date,
    RecurrentOperation,
    THistoryId,
    LoanTransactionAspects,
    SavingTransactionAspects,
)


@dataclass(frozen=True)
class OperationReadResponse:
    id: str
    day: int
    name: str
    amount: float
    transaction_aspects: SavingTransactionAspects | LoanTransactionAspects | None = None

    def __hash__(self) -> int:
        return hash(self.day)


@dataclass(frozen=True)
class HistoryReadResponse:
    date: Date
    recurrent_operations: set[RecurrentOperation]
    operations: set[OperationReadResponse]
    balance: float


class HistoryReader(Generic[TBudgetId, THistoryId]):
    def __init__(self, repository: HistoryRepository) -> None:
        self._repository = repository

    def retrieve(self, id_: THistoryId) -> HistoryReadResponse:
        try:
            history = self._repository.retrieve(id_)
        except CannotRetrieveEntity as err:
            raise BadRequestException(f"History `{id_}` not found") from err
        return HistoryReadResponse(
            date=history.date,
            recurrent_operations=history.recurrent_operations,
            operations={
                OperationReadResponse(
                    id=op.id,
                    day=op.day,
                    name=op.name,
                    amount=op.amount,
                    transaction_aspects=op.transaction_aspects,
                )
                for op in history.operations
            },
            balance=history.balance,
        )

    def list_by_budget(self, id_: TBudgetId) -> list[HistoryReadResponse]:
        histories = self._repository.list_by_budget(id_)

        return [
            HistoryReadResponse(
                date=h.date,
                recurrent_operations=h.recurrent_operations,
                operations={
                    OperationReadResponse(
                        id=op.id,
                        day=op.day,
                        name=op.name,
                        amount=op.amount,
                        transaction_aspects=op.transaction_aspects,
                    )
                    for op in h.operations
                },
                balance=h.balance,
            )
            for h in histories
        ]
