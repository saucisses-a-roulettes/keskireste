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
from abc import ABC, abstractmethod
from typing import Type

from src.shared.application.id import IdFactory
from src.shared.domain.entity import TId
from src.shared.test.domain.mock import MockId


class MockIdFactory(IdFactory[TId], ABC):
    @property
    @abstractmethod
    def id_template(self) -> TId:
        pass

    @id_template.setter
    def id_template(self, id_template: TId) -> None:
        pass


def mock_id_factory(mock_id_class: Type[MockId]):
    def decorator(cls) -> Type:
        class MockIdFactoryBase(cls):
            def __init__(self) -> None:
                self._id_template = mock_id_class("mock_id")

            @property
            def id_template(self) -> MockId:
                return self._id_template

            def generate_id(self) -> MockId:
                return self.id_template

        return MockIdFactoryBase

    return decorator
