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

from typing import Generic, List

import pytest

from shared.application.repository import CannotRetrieveEntity, EntityAlreadyExists
from shared.domain.entity import TEntity, Id
from shared.infrastructure.test.test_entity import MockEntity, MockId


class InMemoryRepository(Generic[TEntity]):
    def __init__(self) -> None:
        self._store: dict[Id, TEntity] = {}

    def add(self, entity: TEntity) -> None:
        if entity.id in self._store:
            raise EntityAlreadyExists(entity.id)
        self._store[entity.id] = entity

    def retrieve(self, id_: Id) -> TEntity:
        try:
            return self._store[id_]
        except KeyError as err:
            raise CannotRetrieveEntity(id_) from err

    def update(self, entity: TEntity) -> None:
        if entity.id not in self._store:
            raise CannotRetrieveEntity(entity.id)
        self._store[entity.id] = entity

    def delete(self, id_: Id) -> None:
        if id_ not in self._store:
            raise CannotRetrieveEntity(id_)
        del self._store[id_]

    def all(self) -> List[TEntity]:
        return list(self._store.values())


def test_add():
    repo = InMemoryRepository()
    entity = MockEntity(MockId("test_id"))

    repo.add(entity)

    with pytest.raises(CannotRetrieveEntity):
        repo.retrieve(MockId("nonexistent_id"))

    assert repo.retrieve(MockId("test_id")) == entity


def test_add_existing():
    repo = InMemoryRepository()
    entity = MockEntity(MockId("test_id"))

    repo.add(entity)

    with pytest.raises(EntityAlreadyExists):
        repo.add(entity)


def test_update():
    repo = InMemoryRepository()
    entity = MockEntity(MockId("test_id"))

    repo.add(entity)

    updated_entity = MockEntity(MockId("test_id"))
    repo.update(updated_entity)

    assert repo.retrieve(MockId("test_id")) == updated_entity


def test_update_nonexistent():
    repo = InMemoryRepository()
    entity = MockEntity(MockId("test_id"))

    with pytest.raises(CannotRetrieveEntity):
        repo.update(entity)


def test_delete():
    repo = InMemoryRepository()
    entity = MockEntity(MockId("test_id"))

    repo.add(entity)
    repo.delete(MockId("test_id"))

    with pytest.raises(CannotRetrieveEntity):
        repo.retrieve(MockId("test_id"))


def test_delete_nonexistent():
    repo = InMemoryRepository()

    with pytest.raises(CannotRetrieveEntity):
        repo.delete(MockId("nonexistent_id"))


def test_all():
    repo = InMemoryRepository()

    entities = [
        MockEntity(MockId("id1")),
        MockEntity(MockId("id2")),
        MockEntity(MockId("id3")),
    ]

    for entity in entities:
        repo.add(entity)

    assert set(repo.all()) == set(entities)
