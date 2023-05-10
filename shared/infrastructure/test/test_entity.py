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
from shared.domain.entity import EntityBase, Id


class MockId(Id):
    def __init__(self, value: str):
        self.value = value

    def __str__(self) -> str:
        return self.value

    def __hash__(self):
        return hash(self.value)

    def __eq__(self, other: object) -> bool:
        return other.__hash__() == self.__hash__() if isinstance(other, Id) else False


class MockEntity(EntityBase[MockId]):
    pass


def test_entity_base_id():
    mock_id = MockId("test_id")
    entity = MockEntity(mock_id)
    assert entity.id == mock_id


def test_entity_base_hash():
    mock_id = MockId("test_id")
    entity = MockEntity(mock_id)
    assert hash(entity) == hash(mock_id)


def test_entity_base_eq():
    mock_id1 = MockId("test_id1")
    mock_id2 = MockId("test_id2")
    entity1 = MockEntity(mock_id1)
    entity2 = MockEntity(mock_id1)
    entity3 = MockEntity(mock_id2)

    assert entity1 == entity2
    assert entity1 != entity3
    assert entity1 != "not_an_entity"
