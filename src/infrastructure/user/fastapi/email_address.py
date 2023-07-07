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
from dependency_injector.wiring import inject, Provide
from fastapi import APIRouter, Depends
from pydantic import BaseModel

from src.application.user.email_address.modifier import UserEmailAddressModifier, UserEmailAddressModificationRequest
from src.application.user.subscription.email_address.validator import EmailAddressValidator
from src.application.user.subscription.emailer import ValidationEmailSender
from src.infrastructure.containers.in_memory import InMemoryContainer
from src.infrastructure.user.id import UserUUID
from src.shared.domain.email import EmailAddress

router = APIRouter()


class _EmailAddressValidationBody(BaseModel):
    email_address: str


@router.post("/user/email_address/validation", status_code=200)
@inject
async def submit_user_email_address_validation(
    body: _EmailAddressValidationBody,
    email_address_validator: EmailAddressValidator = Depends(Provide[InMemoryContainer.email_address_validator]),
) -> None:
    email_address_validator.query(EmailAddress(body.email_address))


class _EmailAddressModificationBody(BaseModel):
    email_address: str
    validation_token: str


@router.put("/user/{user_id}/email_address", status_code=200)
@inject
async def modify_user_email_address(
    user_id: str,
    body: _EmailAddressModificationBody,
    validation_email_sender: ValidationEmailSender = Depends(Provide[InMemoryContainer.validation_email_sender]),
    user_email_address_modifier: UserEmailAddressModifier = Depends(
        Provide[InMemoryContainer.user_email_address_modifier]
    ),
) -> None:
    email_address = EmailAddress(body.email_address)
    validation_email_sender.check_validation_token(email_address, body.validation_token)
    user_email_address_modifier.modify(
        UserEmailAddressModificationRequest(UserUUID(user_id), email_address=email_address)
    )
