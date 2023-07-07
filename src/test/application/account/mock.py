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
import ppa

from src.application.account.repository import AccountRepository
from src.domain.account import AccountId
from src.test.domain.mocks import MockAccountId
from src.shared.application.id import IdFactory
from src.shared.application.repository import EntityAlreadyExists, EntityNotFound


@ppa.in_memory_repository(
    entity_already_exists_exception=EntityAlreadyExists, entity_not_found_exception=EntityNotFound
)
class AccountMockRepository(AccountRepository):
    pass


class MockAccountIdFactory(IdFactory[AccountId]):
    def __init__(self) -> None:
        self._id_template = MockAccountId("mock_id")

    def generate_id(self) -> MockAccountId:
        return self.id_template

    @property
    def id_template(self) -> MockAccountId:
        return self._id_template

    @id_template.setter
    def id_template(self, id_template: MockAccountId) -> None:
        self._id_template = id_template
