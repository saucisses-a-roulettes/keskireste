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
import re
from typing import Any

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends
from pydantic import BaseModel, validator, root_validator

from src.account.application.user.creator import UserCreationRequest, UserCreator
from src.account.application.user.subscription.email_address.validator import EmailAddressValidator
from src.account.application.user.subscription.emailer import ValidationEmailSender
from src.account.domain.user import UserName
from src.account.infrastructure.containers.in_memory import InMemoryContainer
from src.account.infrastructure.user.password.vault import UserPasswordVault
from src.shared.domain.email import EmailAddress

router = APIRouter()


class _SubscriptionQueryBody(BaseModel):
    email_address: str

    @validator("email_address")
    def email_address_validator(cls, email_address: str) -> str:
        EmailAddress(email_address)
        return email_address


@router.post("/query", status_code=201)
@inject
async def submit_user_email_address(
    subscription_body: _SubscriptionQueryBody,
    email_address_validator: EmailAddressValidator = Depends(Provide[InMemoryContainer.email_address_validator]),
) -> None:
    email_address_validator.query(EmailAddress(subscription_body.email_address))


class PasswordNotStrongEnough(ValueError):
    def __init__(self):
        super().__init__("Password is not strong enough")


class _SubscriptionValidationBody(BaseModel):
    username: str
    email_address: str
    password: str
    validation_token: str

    @validator("email_address")
    def email_address_validator(cls, email_address: str) -> str:
        EmailAddress(email_address)
        return email_address

    @validator("username")
    def username_validator(cls, username: str) -> str:
        UserName(username)
        return username

    @validator("password")
    def password_validator(cls, password: str) -> str:
        cls._check_password_strong(password)
        return password

    @root_validator
    def root_validator(cls, values: dict[str, Any]) -> dict[str, Any]:
        email_address, validation_token = values["email_address"], values["validation_token"]
        cls._check_validation_token(validation_token=validation_token, email_address=email_address)
        return values

    @staticmethod
    def _check_password_strong(password: str):
        if (
            len(password) < 8
            or not any(char.isupper() for char in password)
            or not any(char.islower() for char in password)
            or not any(char.isdigit() for char in password)
            or not re.search(r"[@#$%^&+=]", password)
        ):
            raise PasswordNotStrongEnough()

    @staticmethod
    @inject
    def _check_validation_token(
        validation_token: str,
        email_address: str,
        validation_email_sender: ValidationEmailSender = Provide[InMemoryContainer.validation_email_sender],
    ):
        validation_email_sender.check_validation_token(EmailAddress(email_address), validation_token)


@router.post("/validation", status_code=201)
@inject
async def confirm_user_email_address(
    subscription_validation_body: _SubscriptionValidationBody,
    user_creator: UserCreator = Depends(Provide[InMemoryContainer.user_creator]),
    user_password_vault: UserPasswordVault = Depends(Provide[InMemoryContainer.user_password_vault]),
):
    user_creation_request = UserCreationRequest(
        EmailAddress(subscription_validation_body.email_address), UserName(subscription_validation_body.username)
    )
    user_password_vault.save(user_creation_request.email_address, subscription_validation_body.password)

    user_creator.create(user_creation_request)
