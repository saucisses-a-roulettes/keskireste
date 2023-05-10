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
from src.application.budget.saving.account.repository import SavingAccountRepository
from src.domain.budget import TBudgetId
from src.domain.budget.saving.account import TSavingAccountId, SavingAccount


class SavingAccountInMemoryRepository(SavingAccountRepository):
    def __init__(self, saving_accounts: set[SavingAccount] | None) -> None:
        self._saving_accounts: set[SavingAccount] = saving_accounts or set()

    def retrieve(self, id_: TSavingAccountId) -> SavingAccount:
        return next()

    def list_by_budget(self, budget_id: TBudgetId) -> frozenset[SavingAccount]:
        pass

    def save(self, account: SavingAccount) -> None:
        pass

    def delete(self, id_: TSavingAccountId) -> None:
        pass
