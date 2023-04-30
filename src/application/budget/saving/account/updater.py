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
from src.application.repository import CannotRetrieveEntity
from src.domain.budget.saving.account import TSavingAccountId, BalanceReference


@dataclass(frozen=True)
class SavingAccountUpdateRequest(Generic[TSavingAccountId]):
    id: TSavingAccountId
    name: str
    balance: BalanceReference | None = None


class SavingAccountUpdater:
    def __init__(self, repository: SavingAccountRepository) -> None:
        self._repository = repository

    def create(self, request: SavingAccountUpdateRequest) -> None:
        try:
            saving_account = self._repository.retrieve(request.id)
        except CannotRetrieveEntity as e:
            raise ValueError(str(e)) from e

        saving_account.rename(request.name)
        saving_account.update_balance_reference(request.balance)

        self._repository.save(saving_account)
