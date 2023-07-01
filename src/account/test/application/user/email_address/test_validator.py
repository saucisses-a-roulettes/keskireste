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
from src.account.infrastructure.containers.in_memory import InMemoryContainer
from src.account.test.application.user.email_address.mock import ValidationEmailMockSender, EmailAddressCheckerMock
from src.shared.domain.email import EmailAddress


def test_query_email_address(
    container: InMemoryContainer,
    email_address_checker_mock: EmailAddressCheckerMock,
    validation_email_mock_sender: ValidationEmailMockSender,
) -> None:
    email_address_validator = container.email_address_validator(
        email_address_checker=email_address_checker_mock, validation_email_sender=validation_email_mock_sender
    )

    email_address = EmailAddress("correct-format@test.com")

    email_address_validator.query(email_address)

    assert email_address_checker_mock.checked_email_addresses == [email_address]
    assert validation_email_mock_sender.email_sent_to == [email_address]
