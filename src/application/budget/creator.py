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

from shared.domain.entity import Id
from src.application.budget.repository import BudgetRepository
from src.domain.budget import Budget


class BudgetCreator:
    def __init__(self, repository: BudgetRepository) -> None:
        self._repository = repository

    def create(self, id_: Id) -> None:
        self._repository.create(Budget(id_=id_, histories_ids=frozenset()))
