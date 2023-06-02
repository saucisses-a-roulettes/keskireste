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
from abc import ABC

from src.account.domain.account import AccountId
from src.shared.domain.entity import EntityBase, TId, Id


class TransactionId(Id, ABC):
    pass


class Transaction(EntityBase[TId]):
    def __init__(self, id_: TId, account_id: AccountId, date: datetime.date, label: str, amount: float) -> None:
        super().__init__(id_)
        self._account_id = account_id
        self._date = date
        self._label = label
        self._amount = amount

    @property
    def account_id(self) -> AccountId:
        return self._account_id

    @property
    def date(self) -> datetime.date:
        return self._date

    @property
    def label(self) -> str:
        return self._label

    @property
    def amount(self) -> float:
        return self._amount

    def rectify_date(self, new_date: datetime.date) -> None:
        self._date = new_date

    def rectify_amount(self, new_amount: float) -> None:
        self._amount = new_amount

    def modify_label(self, new_label: str) -> None:
        self._label = new_label
