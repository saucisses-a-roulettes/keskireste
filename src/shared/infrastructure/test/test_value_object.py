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


from src.shared.domain.value_object import ValueObject


class MockValueObject(ValueObject):
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y


class OtherValueObject(ValueObject):
    def __init__(self, x: int, y: int):
        self.x = x
        self.y = y


def test_value_object_equality():
    obj1 = MockValueObject(1, 2)
    obj2 = MockValueObject(1, 2)
    obj3 = MockValueObject(2, 3)
    other_obj = OtherValueObject(1, 2)

    assert obj1 == obj2
    assert obj1 != obj3
    assert obj1 != other_obj
    assert obj1 != "not a value object"


def test_value_object_hash():
    obj1 = MockValueObject(1, 2)
    obj2 = MockValueObject(1, 2)
    obj3 = MockValueObject(2, 3)

    assert hash(obj1) == hash(obj2)
    assert hash(obj1) != hash(obj3)

    # Ensure that the objects can be used as dictionary keys
    d = {obj1: "obj1", obj2: "obj2", obj3: "obj3"}
    assert d[obj1] == "obj2"
    assert d[obj2] == "obj2"
    assert d[obj3] == "obj3"
