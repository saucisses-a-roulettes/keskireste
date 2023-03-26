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

from typing import Awaitable, Callable, Dict, Union

from nicegui import background_tasks, ui
from nicegui.dependencies import register_component

register_component("router_frame", __file__, "router_frame.js")


class Router:
    def __init__(self) -> None:
        self.routes: Dict[str, Callable] = {}
        self.content: ui.element | None = None

    def add(self, path: str):
        def decorator(func: Callable):
            self.routes[path] = func
            return func

        return decorator

    def open(self, target: Union[Callable, str]):
        if isinstance(target, str):
            path = target
            builder = self.routes[target]
        else:
            path = {v: k for k, v in self.routes.items()}[target]
            builder = target

        async def build():
            with self.content:
                await ui.run_javascript(f'history.pushState({{page: "{path}"}}, "", "{path}")', respond=False)
                result = builder()
                if isinstance(result, Awaitable):
                    await result

        self.content.clear()
        background_tasks.create(build())

    def frame(self) -> ui.element:
        self.content = ui.element("router_frame").on("open", lambda msg: self.open(msg["args"]))
        return self.content
