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

from src.application.user.subscription.email_address.validator import EmailAddressValidator
from src.infrastructure.containers.in_memory import InMemoryContainer
from src.shared.domain.email import EmailAddress

router = APIRouter()


class _EmailAddressValidationBody(BaseModel):
    email_address: str


@router.post("/validation", status_code=200)
@inject
async def submit_user_email_address_validation(
    body: _EmailAddressValidationBody,
    email_address_validator: EmailAddressValidator = Depends(Provide[InMemoryContainer.email_address_validator]),
) -> None:
    email_address_validator.query(EmailAddress(body.email_address))
