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

from src.application.budget.history.repository import HistoryRepository
from src.domain.budget.history import (
    Date,
    History,
    RecurrentOperation,
    LoanTransactionAspects,
    SavingTransactionAspects,
    Operation,
)
from src.domain.entity import Id


@dataclass(frozen=True)
class OperationCreationRequest:
    id: str
    day: int
    name: str
    amount: float
    transaction_aspects: SavingTransactionAspects | LoanTransactionAspects | None = None


@dataclass(frozen=True)
class HistoryCreationRequest:
    id_: Id
    date: Date
    recurrent_operations: set[RecurrentOperation]
    operations: set[OperationCreationRequest]


class HistoryCreator:
    def __init__(self, repository: HistoryRepository) -> None:
        self._repository = repository

    def create(self, request: HistoryCreationRequest) -> None:
        self._repository.create(
            History(
                id_=request.id_,
                date=request.date,
                recurrent_operations=request.recurrent_operations,
                operations={
                    Operation(
                        id_=op.id,
                        day=op.day,
                        name=op.name,
                        amount=op.amount,
                        transaction_aspects=op.transaction_aspects,
                    )
                    for op in request.operations
                },
            )
        )
