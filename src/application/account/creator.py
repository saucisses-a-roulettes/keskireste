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

from src.application.account.repository import AccountRepository, AccountAlreadyExists
from src.domain.account import Account, AccountName, AccountId
from src.domain.user import UserId
from src.shared.application.id import IdFactory
from src.shared.application.repository import EntityAlreadyExists


@dataclass(frozen=True)
class AccountCreationRequest:
    user_id: UserId
    name: AccountName
    reference_balance: float


class AccountCreator:
    def __init__(self, repository: AccountRepository, id_factory: IdFactory[AccountId]) -> None:
        self._repository = repository
        self._id_factory = id_factory

    def create(self, request: AccountCreationRequest) -> None:
        account = Account(
            id_=self._id_factory.generate_id(),
            user_id=request.user_id,
            name=request.name,
            reference_balance=request.reference_balance,
        )

        try:
            self._repository.add(account)
        except EntityAlreadyExists as e:
            raise AccountAlreadyExists(account_id=account.id) from e
