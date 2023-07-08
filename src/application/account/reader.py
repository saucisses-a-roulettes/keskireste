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

from src.application.account.repository import AccountRepository, AccountNotFound
from src.domain.account import AccountId, AccountName
from src.domain.user import UserId
from src.shared.application.repository import EntityNotFound


@dataclass(frozen=True)
class AccountRetrievalResponse:
    id: AccountId
    user_id: UserId
    name: AccountName
    reference_balance: float


class AccountReader:
    def __init__(self, repository: AccountRepository) -> None:
        self._repository = repository

    def retrieve(self, account_id: AccountId) -> AccountRetrievalResponse:
        try:
            account = self._repository.retrieve(account_id)
        except EntityNotFound as e:
            raise AccountNotFound(account_id=account_id) from e

        return AccountRetrievalResponse(
            id=account.id, user_id=account.user_id, name=account.name, reference_balance=account.reference_balance
        )
