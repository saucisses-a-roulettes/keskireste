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
import pytest

from src.infrastructure.containers.in_memory import InMemoryContainer
from src.test.application.user.email_address.mock import ValidationEmailMockSender, EmailAddressCheckerMock


@pytest.fixture
def validation_email_mock_sender(container: InMemoryContainer):
    return ValidationEmailMockSender()


@pytest.fixture
def email_address_checker_mock(container: InMemoryContainer):
    return EmailAddressCheckerMock()


@pytest.fixture
def user_email_address_modifier(container: InMemoryContainer):
    return container.user_email_address_modifier()
