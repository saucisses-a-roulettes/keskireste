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
from src.domain.account import AccountName, AccountId
from src.shared.application.repository import EntityNotFound


@dataclass(frozen=True)
class AccountUpdateRequest:
    id: AccountId
    name: AccountName
    reference_balance: float


class AccountUpdater:
    def __init__(self, repository: AccountRepository) -> None:
        self._repository = repository

    def update(self, request: AccountUpdateRequest) -> None:
        try:
            account = self._repository.retrieve(request.id)
        except EntityNotFound as e:
            raise AccountNotFound(account_id=request.id) from e

        account.rename(request.name)
        account.modify_reference_balance(request.reference_balance)

        self._repository.update(account)
