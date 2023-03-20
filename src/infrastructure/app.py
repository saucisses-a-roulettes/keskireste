import urllib.parse
from dataclasses import dataclass
from src.application.history.creator import HistoryCreator
from router import Router
from nicegui import ui
from src.application.history.reader import History, HistoryReader
from src.infrastructure.history.repository import HistoryPickleRepository


router = Router()


def __init__(self) -> None:
    pass


@ui.page("/")
@ui.page("/{_:path}")
async def route():
    ui.label("KeskiReste")
    # with ui.row():
    #     ui.button("Create", on_click=lambda: router.open(history_creation))
    #     ui.button("Open", on_click=lambda: router.open(show_two))

    # this places the content which should be displayed
    router.frame().classes("w-full p-4 bg-gray-100")


ui.run()


@router.add("/")
async def home():
    ui.label("KeskiReste")
    with ui.row():
        ui.button("Create", on_click=lambda: router.open(history_creation))
        # ui.button("Open", on_click=lambda: router.open(show_two))


class HistoryCreation(ui.column):
    def __init__(self, history_creator: HistoryCreator) -> None:
        super().__init__()
        self._history_creator = history_creator

        @dataclass
        class _Path:
            value: str

        path = _Path("")
        ui.label("Bank Creation")
        ui.input(label="Path", placeholder="~/").bind_value(path)

        def _create_history(p: str) -> None:
            self._history_creator.create(p)
            router.open(f"/history/view/{urllib.parse.quote(p)}")

        ui.button("Create", on_click=lambda: _create_history(path.value))


@router.add("/history/creation")
async def history_creation():
    HistoryCreation(history_creator=HistoryCreator(repository=HistoryPickleRepository()))


# class HistoryOpening(ui.column):
#     def __init__(self, history_reader: HistoryReader) -> None:
#         super().__init__()
#         self._history_reader = history_reader
#
#         @dataclass
#         class _Path:
#             value: str
#
#         path = _Path("")
#         ui.label("Bank Creation")
#         ui.input(label="Path", placeholder="~/").bind_value(path)
#
#         # ui.button("Create", on_click=lambda: self._history_creator.create(path.value))
#
#
# @router.add("/history/opening")
# async def history_opening():
#     @dataclass
#     class _Path:
#         value: str
#
#     path = _Path("")
#
#     ui.label("Bank Creation")
#     ui.input(
#         label="Path",
#         placeholder="~/",
#         validation={"Empty Path": lambda value: len(value) > 1},
#     ).bind_value(path)
#     # ui.button("Open", on_click=lambda: open_bank(Path(path.value)))
#     # ui.button("Open Ratounet", on_click=lambda: open_bank(Path("~/test_ratounet_bank")))


class HistoryView(ui.column):
    def __init__(self, path: str, history_reader: HistoryReader) -> None:
        super().__init__()
        self._history_reader = history_reader
        history: History = self._history_reader.retrieve(path)
        ui.label(history.path)


@router.add("/history/view/{path}")
async def history_view(path: str):
    HistoryView(path=path, history_reader=HistoryReader(repository=HistoryPickleRepository()))


# @router.add("/three")
# async def show_three():
#     ui.label("Content Three").classes("text-2xl")
