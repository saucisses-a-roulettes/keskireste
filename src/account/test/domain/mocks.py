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
from src.account.domain.account import AccountId, UserId
from src.account.domain.recurring_transaction import RecurringTransactionId
from src.shared.domain.entity import IdBase


class RecurringTransactionMockId(RecurringTransactionId, IdBase[str]):
    pass


class MockAccountId(AccountId, IdBase[str]):
    pass


class MockUserId(UserId, IdBase[str]):
    pass


class MockId(IdBase[str]):
    pass
