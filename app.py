import datetime
import json
from dataclasses import dataclass
from typing import Any, TypedDict
import fire
import pickle
import pandas as pd
from nicegui import ui
import pathlib


class Data(TypedDict):
    monthly_income: pd.DataFrame
    monthly_expense: pd.DataFrame
    expenses: pd.DataFrame


class Path:
    def __init__(self, value: str) -> None:
        if value.startswith("~/"):
            value = value.replace("~", str(pathlib.Path.home()), 1)
        self._value = value

    @property
    def value(self) -> str:
        return self._value

    def __str__(self) -> str:
        return self._value

    @property
    def name(self) -> str:
        return self.value.split("/")[-1]


class BankManager:
    def __init__(self) -> None:
        self._data: Data | None = None

    def create(self, path: str) -> None:
        data = Data(
            monthly_income=pd.DataFrame(columns=["name", "value"]),
            monthly_expense=pd.DataFrame(columns=["name", "value"]),
            expenses=pd.DataFrame(columns=["name", "date", "value"]),
        )
        with open(path, "w+b") as f:
            pickle.dump(data, f)

    def open(self, path: str) -> None:
        with open(path, "rb") as f:
            self._data = pickle.load(f)

    #
    # def _save(self, path: str, data: Data) -> None:
    #     with open(path, 'wb') as f:
    #         pickle.dump(data, f)
    #
    #
    # def add_monthly_expense(self, path: str, name: str, value: float) -> None:
    #     data = self._load(path)
    #
    #     if data['monthly_expense']['name'].str.contains(name).any():
    #         raise ValueError(f'`{name}` is already assign to another values')
    #
    #     data['monthly_expense'] = pd.concat([data['monthly_expense'], pd.DataFrame([pd.Series({'name': name, 'value': value})])])
    #
    #     self._save(path, data)
    #
    # def _add_expense(self, data: Data, name: str, date: datetime.date, value: float) -> None:
    #     data['expenses'] = pd.concat([data['expenses'], pd.DataFrame([pd.Series({'name': name, 'date': datetime.date, 'value': value})])])
    #
    def show(self) -> str:
        monthly_income = self._data["monthly_income"]["value"].sum()
        monthly_expense = self._data["monthly_expense"]["value"].sum()
        return f"Monthly income : {monthly_income:.2f}\nMonthly expense: {monthly_expense:.2f}\nBudget: {monthly_income - monthly_expense:.2f}"

    def monthly_incomes(self) -> list[dict[str, Any]]:
        return self._data["monthly_income"].to_dict("records")


manager = BankManager()


def create_bank(path: Path) -> None:
    manager.create(str(path))
    manager.open(str(path))
    ui.open(target=lambda: bank(str(path)))


@ui.page("/")
def home():
    ui.label("KeskiReste")
    ui.button("Create", on_click=lambda: ui.open(bank_creation))
    ui.button("Open", on_click=lambda: ui.open(bank_opening))


@ui.page("/bank/creation")
def bank_creation():
    @dataclass
    class _Path:
        value: str

    path = _Path("")

    ui.label("Bank Creation")
    ui.input(
        label="Path",
        placeholder="~/",
        validation={"Empty Path": lambda v: len(v) < 1},
    ).bind_value(path)
    ui.button("Create", on_click=lambda: create_bank(Path(path.value)))


def open_bank(path: Path) -> None:
    manager.open(str(path))
    ui.open(target=f"{path.value.split('/')[-1]}")


@ui.page("/bank/open")
def bank_opening():
    @dataclass
    class _Path:
        value: str

    path = _Path("")

    ui.label("Bank Creation")
    ui.input(
        label="Path",
        placeholder="~/",
        validation={"Empty Path": lambda value: len(value) > 1},
    ).bind_value(path)
    ui.button("Open", on_click=lambda: open_bank(Path(path.value)))
    ui.button("Open Ratounet", on_click=lambda: open_bank(Path("~/test_ratounet_bank")))


@ui.page("/bank/{name}")
def bank(name: str):
    ui.label(name)
    ui.label(manager.show())

    incomes = manager.monthly_incomes()

    ui.aggrid({"rowData": incomes})


ui.run()
