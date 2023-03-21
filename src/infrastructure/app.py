import datetime
import pandas as pd
from dataclasses import dataclass
from typing import Any, Self
from src.application.history.creator import HistoryCreator
from router import Router
from nicegui import ui
from src.application.history.reader import History, HistoryReader
from src.application.history.updater import HistoryUpdateRequest, HistoryUpdater
from src.domain.history import Operation, RecurrentOperation
from src.infrastructure.history.repository import HistoryPickleRepository


router = Router()
current_path: str | None = "test"


@dataclass
class InputValue:
    value: str


@dataclass
class Var:
    value: Any

    def set_value(self, v: Any):
        self.value = v


@ui.page("/")
@ui.page("/{_:path}")
async def route():
    ui.label("KeskiReste")
    # with ui.row():
    #     ui.button("Create", on_click=lambda: router.open(history_creation))
    #     ui.button("Open", on_click=lambda: router.open(show_two))

    # this places the content which should be displayed
    router.frame().classes("w-full p-4 bg-gray-100")


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
            global current_path
            self._history_creator.create(p)
            current_path = p
            router.open(history)

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


@dataclass
class HistoryModel:
    path: str
    recurrent_incomes: set[RecurrentOperation]
    recurrent_expenses: set[RecurrentOperation]
    operations: set[Operation]
    filtered_operations: set[str]

    @classmethod
    def from_application(cls, h: History) -> Self:
        return cls(
            path=h.path,
            recurrent_incomes=h.recurrent_incomes,
            recurrent_expenses=h.recurrent_expenses,
            operations=h.operations,
            filtered_operations=h.filtered_operations,
        )

    @property
    def budget(self) -> float:
        ops = self.recurrent_incomes | self.recurrent_expenses
        return sum(o.value for o in ops) + sum(op.value for op in self.operations)


def save_history(h: HistoryModel):
    history_updater = HistoryUpdater(repository=HistoryPickleRepository())

    request = HistoryUpdateRequest(
        path=h.path, recurrent_operations=h.recurrent_incomes | h.recurrent_expenses, operations=h.operations
    )

    history_updater.update(request)


def add_recurrent_operation(h: HistoryModel, op: RecurrentOperation):
    if op.value < 0:
        h.recurrent_expenses.add(op)
    elif op.value > 0:
        h.recurrent_incomes.add(op)
    save_history(h)
    router.open(history)


def delete_recurrent_income(h: HistoryModel, selected_income: Any):
    print(selected_income)
    if selected_income:
        print(selected_income)
        year = int(selected_income["period"].split("/")[0])
        month = int(selected_income["period"].split("/")[1])
        name = selected_income["name"]
        h.recurrent_incomes = {r for r in h.recurrent_incomes if r.year != year or r.month != month or r.name != name}
        save_history(h)
        router.open(history)


def delete_recurrent_expense(h: HistoryModel, selected_expense: Any):
    print(selected_expense)
    if selected_expense:
        print(selected_expense)
        year = int(selected_expense["period"].split("/")[0])
        month = int(selected_expense["period"].split("/")[1])
        name = selected_expense["name"]
        h.recurrent_expenses = {r for r in h.recurrent_expenses if r.year != year or r.month != month or r.name != name}
        save_history(h)
        router.open(history)


def add_operations_from_csv(path: str, h: HistoryModel) -> None:
    data = pd.read_csv(path, skiprows=6, encoding="ISO-8859-1", sep=";")
    data = data.rename(columns={"Date": "date", "Libellé": "name", "Montant(EUROS)": "value"})

    h.operations.update(
        {
            Operation(
                date=datetime.datetime.strptime(d["date"], "%d/%m/%Y"),
                name=d["name"],
                value=float(d["value"].replace(",", ".")),
            )
            for d in data.to_dict("records")
        }
    )
    save_history(h)
    router.open(history)


@router.add("/history")
async def history():
    if not current_path:
        router.open("/")
    history_reader = HistoryReader(repository=HistoryPickleRepository())
    history_model = HistoryModel.from_application(history_reader.retrieve(current_path))
    with ui.column():
        ui.label(history_model.path).classes("capitalize")
        with ui.row():
            with ui.column():
                with ui.column():
                    op_name = InputValue("")
                    op_amount = InputValue("")
                    op_date = InputValue("")
                    ui.label("add recurrent operation")
                    with ui.row():
                        ui.input(label="Month", placeholder="2023/01").bind_value(op_date)
                        ui.input(label="Name", placeholder="Salary").bind_value(op_name)
                        ui.input(label="Amount", placeholder="1688,45").bind_value(op_amount)
                        ui.button(
                            text="Add",
                            on_click=lambda: add_recurrent_operation(
                                h=history_model,
                                op=RecurrentOperation(
                                    year=int(op_date.value.split("/")[0]),
                                    month=int(op_date.value.split("/")[1]),
                                    name=op_name.value,
                                    value=float(op_amount.value),
                                ),
                            ),
                        )
                    ui.button("Open", on_click=lambda: add_operations_from_csv("test_bank.csv", history_model))

            with ui.column():
                selected_income = Var(None)

                ui.table(
                    title="Recurrent Incomes",
                    columns=[
                        {
                            "name": "period",
                            "label": "Period",
                            "field": "period",
                            "required": True,
                            "sortable": True,
                        },
                        {
                            "name": "name",
                            "label": "Name",
                            "field": "name",
                            "required": True,
                            "align": "left",
                        },
                        {"name": "amount", "label": "Amount", "field": "amount", "required": True, "sortable": True},
                    ],
                    rows=[
                        {"period": f"{r.year}/{r.month}", "name": r.name, "amount": r.value}
                        for r in history_model.recurrent_incomes
                    ],
                    selection="single",
                    on_select=lambda e: selected_income.set_value(e.selection[0]),
                ).on(
                    "keydown.delete",
                    lambda: delete_recurrent_income(h=history_model, selected_income=selected_income.value),
                )
                selected_expense = Var(None)
                ui.table(
                    title="Recurrent Expenses",
                    columns=[
                        {
                            "name": "period",
                            "label": "Period",
                            "field": "period",
                            "required": True,
                            "sortable": True,
                        },
                        {
                            "name": "name",
                            "label": "Name",
                            "field": "name",
                            "required": True,
                            "align": "left",
                        },
                        {"name": "amount", "label": "Amount", "field": "amount", "required": True, "sortable": True},
                    ],
                    rows=[
                        {"period": f"{r.year}/{r.month}", "name": r.name, "amount": r.value}
                        for r in history_model.recurrent_expenses
                    ],
                    selection="single",
                    on_select=lambda e: selected_expense.set_value(e.selection[0]),
                ).on(
                    "keydown.delete",
                    lambda: delete_recurrent_expense(h=history_model, selected_expense=selected_expense.value),
                )
            with ui.column().classes("w-1/2"):
                ui.table(
                    title="Last Operations",
                    columns=[
                        {
                            "name": "date",
                            "label": "Date",
                            "field": "date",
                            "required": True,
                            "sortable": True,
                        },
                        {
                            "name": "name",
                            "label": "Name",
                            "field": "name",
                            "required": True,
                            "sortable": True,
                            "align": "left",
                        },
                        {"name": "amount", "label": "Amount", "field": "amount", "sortable": True, "required": True},
                    ],
                    rows=[{"date": o.date, "name": o.name, "amount": o.value} for o in history_model.operations],
                    pagination=10,
                )
        ui.label(f"Budget: {history_model.budget}")


# @router.add("/three")
# async def show_three():
#     ui.label("Content Three").classes("text-2xl")

ui.run()
