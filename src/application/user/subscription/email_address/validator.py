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
from src.application.user.subscription.email_address.checker import EmailAddressChecker
from src.application.user.subscription.emailer import ValidationEmailSender
from src.shared.domain.email import EmailAddress


class EmailAddressValidator:
    def __init__(
        self,
        email_address_checker: EmailAddressChecker,
        validation_email_sender: ValidationEmailSender,
    ) -> None:
        self._email_address_checker = email_address_checker
        self._validation_email_sender = validation_email_sender

    def query(self, email_address: EmailAddress) -> None:
        self._email_address_checker.check(email_address)
        self._validation_email_sender.send(email_address)
