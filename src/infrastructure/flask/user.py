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
#
#
# class TestId(IdBase):
#     def __str__(self) -> str:
#         pass
#
#     def __hash__(self):
#         pass
#
#
# class Test2Id(Id):
#     def __str__(self) -> str:
#         pass
#
#     def __hash__(self):
#         pass
#
#
# class UserInMemoryRepository(UserRepository[TestId]):
#     def retrieve(self, user: TestId) -> User:
#         pass
#
#     def save(self, user: User) -> None:
#         pass
#
#
# def get_user(user_id: str):
#     user_reader: UserReader[Test2Id] = UserReader(repository=UserTestRepository())
#
#     user_response = user_reader.retrieve(user_id)
#
#     return ...
