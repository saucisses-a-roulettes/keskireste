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

from fastapi import FastAPI

from .account.fastapi.post import router as account_post_router
from .containers.in_memory import InMemoryContainer


def create_app() -> FastAPI:
    new_app = FastAPI()
    container = InMemoryContainer()
    container.init_resources()
    container.wire(modules=["src.account.infrastructure.account.fastapi.post"])
    new_app.container = container  # type: ignore
    new_app.include_router(account_post_router, prefix="/account")
    return new_app


app = create_app()
