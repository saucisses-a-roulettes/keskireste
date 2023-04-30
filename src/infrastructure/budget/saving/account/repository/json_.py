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
import json
import uuid
from typing import cast

from src.application.budget.saving.account.repository import SavingAccountRepository
from src.application.repository import CannotRetrieveEntity
from src.domain.budget.history import Date
from src.domain.budget.saving.account import TSavingAccountId, SavingAccount, BalanceReference
from src.domain.entity import Id
from src.infrastructure.budget.repository.json_ import (
    BudgetDictModel,
    SavingAccountDictModel,
    BalanceReferenceDictModel,
)
from src.infrastructure.budget.repository.model import BudgetPath


class SavingAccountId(Id):
    def __init__(self, uuid_id: uuid.UUID, budget_path: BudgetPath):
        self._uuid_id = uuid_id
        self._budget_path = budget_path

    @property
    def budget_path(self) -> BudgetPath:
        return self._budget_path

    def __str__(self) -> str:
        return self._uuid_id.hex

    def __hash__(self) -> int:
        return hash(self._uuid_id)

    def __eq__(self, other: object) -> bool:
        return self._uuid_id == other._uuid_id if isinstance(other, SavingAccountId) else False


class SavingAccountJsonRepository(SavingAccountRepository[BudgetPath, SavingAccountId]):
    @staticmethod
    def _parse_saving_account_dict(budget_path: BudgetPath, sa_dict: SavingAccountDictModel) -> SavingAccount:
        return SavingAccount(
            id_=SavingAccountId(uuid_id=uuid.UUID(sa_dict["id"]), budget_path=budget_path),
            name=sa_dict["name"],
            balance=BalanceReference(
                balance=sa_dict["balance_reference"]["balance"],
                date=Date(year=sa_dict["balance_reference"]["year"], month=sa_dict["balance_reference"]["month"]),
            ),
        )

    @staticmethod
    def _serialize_account(sa: SavingAccount) -> SavingAccountDictModel:
        return SavingAccountDictModel(
            id=str(sa.id),
            name=sa.name,
            balance_reference=BalanceReferenceDictModel(
                balance=sa.balance_reference.balance,
                month=sa.balance_reference.date.month,
                year=sa.balance_reference.date.year,
            ),
        )

    def retrieve(self, id_: SavingAccountId) -> SavingAccount:
        path = str(id_.budget_path)
        with open(path, "r") as f:
            model = cast(BudgetDictModel, json.load(f))

        try:
            return next(
                self._parse_saving_account_dict(id_.budget_path, sa_dict)
                for sa_dict in model["saving_accounts"]
                if SavingAccountId(uuid_id=uuid.UUID(sa_dict["id"]), budget_path=id_.budget_path) == id_
            )
        except StopIteration as err:
            raise CannotRetrieveEntity(id_) from err

    def list_by_budget(self, budget_id: BudgetPath) -> frozenset[SavingAccount]:
        path = str(budget_id)
        with open(path, "r") as f:
            model = cast(BudgetDictModel, json.load(f))

        return frozenset(self._parse_saving_account_dict(budget_id, sa_dict) for sa_dict in model["saving_accounts"])

    def save(self, account: SavingAccount) -> None:
        path = str(account.id.budget_path)
        saving_account_model = self._serialize_account(account)
        with open(path, "r") as f:
            model = cast(BudgetDictModel, json.load(f))
        saving_accounts = model["saving_accounts"]
        saving_accounts.append(saving_account_model)
        with open(path, "w") as f:
            json.dump(model, f)

    def delete(self, id_: TSavingAccountId) -> None:
        path = str(id_.budget_path)
        with open(path, "r") as f:
            model = cast(BudgetDictModel, json.load(f))
        model["saving_accounts"] = [sa for sa in model["saving_accounts"] if sa["id"] != str(id_)]
        with open(path, "w") as f:
            json.dump(model, f)
