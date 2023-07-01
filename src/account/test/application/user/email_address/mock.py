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
from src.account.application.user.subscription.email_address.checker import EmailAddressChecker
from src.account.application.user.subscription.emailer import ValidationEmailSender
from src.shared.domain.email import EmailAddress


class ValidationEmailMockSender(ValidationEmailSender):
    def __init__(self) -> None:
        self._email_sent_to: list[EmailAddress] = []

    def send(self, email_address: EmailAddress) -> None:
        self._email_sent_to.append(email_address)

    @property
    def email_sent_to(self) -> list[EmailAddress]:
        return self._email_sent_to


class EmailAddressCheckerMock(EmailAddressChecker):
    def __init__(self) -> None:
        self._checked_email_addresses: list[EmailAddress] = []

    def check(self, email_address: EmailAddress) -> None:
        self._checked_email_addresses.append(email_address)

    @property
    def checked_email_addresses(self) -> list[EmailAddress]:
        return self._checked_email_addresses
