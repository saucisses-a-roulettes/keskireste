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

from src.application.budget.saving.account.repository import SavingAccountRepository
from src.domain.budget.saving.account import TSavingAccountId, BalanceReference
from src.domain.entity import EntityNotFound


@dataclass(frozen=True)
class SavingAccountReadResponse(Generic[TSavingAccountId]):
    id: TSavingAccountId
    name: str
    balance: BalanceReference | None = None


class SavingAccountReader(Generic[TSavingAccountId]):
    def __init__(self, repository: SavingAccountRepository) -> None:
        self._repository = repository

    def retrieve(self, id_: TSavingAccountId) -> SavingAccountReadResponse:
        try:
            saving_account = self._repository.retrieve(id_)
        except EntityNotFound as e:
            raise ValueError(str(e)) from e
        return SavingAccountReadResponse(
            id=saving_account.id,
            name=saving_account.name,
            balance=saving_account.balance_reference,
        )

    def list_all(self) -> frozenset[SavingAccountReadResponse]:
        saving_accounts = self._repository.list_by_budget()
        return frozenset(
            SavingAccountReadResponse(
                id=sa.id,
                name=sa.name,
                balance=sa.balance_reference,
            )
            for sa in saving_accounts
        )
