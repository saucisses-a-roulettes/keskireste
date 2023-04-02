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

import datetime
from typing import Mapping
from PySide6.QtCore import QMetaObject, Signal
from PySide6.QtGui import QStandardItem, QStandardItemModel
from PySide6.QtWidgets import QComboBox, QHBoxLayout, QLabel, QSizePolicy, QStackedWidget, QVBoxLayout, QWidget
from src.application.budget.history.creator import HistoryCreationRequest, HistoryCreator
from src.application.budget.history.reader import HistoryReadResponse, HistoryReader
from src.application.budget.history.updater import HistoryUpdateRequest, HistoryUpdater
from src.application.exception import BadRequestException
from src.domain.history import Date, RecurrentOperation
from src.infrastructure.budget.history.repository.json_ import HistoryJsonRepository
from src.infrastructure.budget.history.repository.model import HistoryId
from src.infrastructure.budget.repository.model import BudgetPath
from src.infrastructure.pyside.history.operations import HistoryOperationsManagerWidget
from src.infrastructure.pyside.history.dashboard import HistoryDashboardWidget


def retrieve_or_create_history(history_id: HistoryId) -> HistoryReadResponse:
    reader = HistoryReader(repository=HistoryJsonRepository())
    creator = HistoryCreator(repository=HistoryJsonRepository())
    try:
        history = reader.retrieve(history_id)
    except BadRequestException:
        creator.create(
            HistoryCreationRequest(id_=history_id, date=history_id.date, recurrent_operations=set(), operations=set())
        )
        history = reader.retrieve(history_id)
    return history


class DatePicker(QWidget):
    MONTHS: Mapping[str, int] = {
        "January": 1,
        "February": 2,
        "March": 3,
        "April": 4,
        "May": 5,
        "June": 6,
        "July": 7,
        "August": 8,
        "September": 9,
        "October": 10,
        "November": 11,
        "December": 12,
    }

    date_changed = Signal(Date)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        layout = QHBoxLayout(self)
        self.year_selector = QComboBox(self)
        model = QStandardItemModel()
        current_year: int = datetime.datetime.now().year
        for i in range(10):
            model.appendRow(QStandardItem(str(current_year - i)))
        self.year_selector.setModel(model)
        layout.addWidget(self.year_selector)

        self.month_selector = QComboBox(self)
        model = QStandardItemModel()
        for month in self.MONTHS:
            model.appendRow(QStandardItem(month))
        self.month_selector.setModel(model)
        current_month = datetime.datetime.now().month
        self.month_selector.setCurrentText(next(key for key, value in self.MONTHS.items() if value == current_month))
        layout.addWidget(self.month_selector)

        self._connect_signals()

    def _connect_signals(self) -> None:
        self.year_selector.currentTextChanged.connect(self._on_date_changed)
        self.month_selector.currentTextChanged.connect(self._on_date_changed)

    def _on_date_changed(self) -> None:
        date = Date(int(self.year_selector.currentText()), self.MONTHS[self.month_selector.currentText()])
        self.date_changed.emit(date)

    def refresh(self, date: Date) -> None:
        self.year_selector.setCurrentText(date.year)
        self.month_selector.setCurrentText(date.month)

    def retrieve_current_date(self) -> Date:
        return Date(int(self.year_selector.currentText()), self.MONTHS[self.month_selector.currentText()])


class NoHistorySelectedWidget(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.test = QLabel("Sélectionne un budget !", self)


class HistoryWidget(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        QMetaObject.connectSlotsByName(self)

        self.budget_path: BudgetPath | None = None

        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        layout = QVBoxLayout(self)

        self._date_picker = DatePicker()
        layout.addWidget(self._date_picker)

        self._stacked_widget = QStackedWidget()
        layout.addWidget(self._stacked_widget)
        self._history_dashboard = HistoryDashboardWidget()
        self._stacked_widget.addWidget(self._history_dashboard)
        self._history_operations_manager = HistoryOperationsManagerWidget()
        self._stacked_widget.addWidget(self._history_operations_manager)

        self._connect_signals()

    def _connect_signals(self) -> None:
        self._date_picker.date_changed.connect(self._refresh)
        self._history_dashboard.manage_operations_button_clicked.connect(
            lambda: self._stacked_widget.setCurrentWidget(self._history_operations_manager)
        )
        self._history_operations_manager.show_dashboard_button_clicked.connect(
            lambda: self._stacked_widget.setCurrentWidget(self._history_dashboard)
        )
        self._history_operations_manager.add_recurrent_operations_clicked.connect(self._add_recurrent_operation)
        self._history_operations_manager.delete_selected_recurrent_operations_clicked.connect(
            self._delete_recurrent_operation
        )
        self._history_operations_manager.copy_operations_from_previous_month_clicked.connect(
            self._copy_recurrent_operation_from_previous_month
        )

    def _refresh(self) -> None:
        history_id = HistoryId(self.budget_path, self._date_picker.retrieve_current_date())
        history = retrieve_or_create_history(history_id)
        self._history_dashboard.refresh(frozenset(history.recurrent_operations), frozenset(history.operations))
        self._history_operations_manager.refresh(frozenset(history.recurrent_operations), frozenset(history.operations))

    def refresh(self, budget_path: BudgetPath) -> None:
        self.budget_path = budget_path
        self._refresh()

    def _add_recurrent_operation(self, op: RecurrentOperation) -> None:
        reader = HistoryReader(repository=HistoryJsonRepository())
        updater = HistoryUpdater(repository=HistoryJsonRepository())
        history_id = HistoryId(self.budget_path, self._date_picker.retrieve_current_date())
        history = reader.retrieve(history_id)
        request = HistoryUpdateRequest(
            id_=history_id,
            recurrent_operations=history.recurrent_operations | {op},
            operations=history.operations,
        )
        updater.update(request)
        self._refresh()

    def _delete_recurrent_operation(self, ops: set[RecurrentOperation]) -> None:
        reader = HistoryReader(repository=HistoryJsonRepository())
        updater = HistoryUpdater(repository=HistoryJsonRepository())
        history_id = HistoryId(self.budget_path, self._date_picker.retrieve_current_date())
        history_response = reader.retrieve(history_id)

        request = HistoryUpdateRequest(
            id_=history_id,
            recurrent_operations=history_response.recurrent_operations - ops,
            operations=history_response.operations,
        )
        updater.update(request)
        self._refresh()

    def _copy_recurrent_operation_from_previous_month(self) -> None:
        print("LALALA")
        reader = HistoryReader(repository=HistoryJsonRepository())
        updater = HistoryUpdater(repository=HistoryJsonRepository())
        history_id = HistoryId(self.budget_path, self._date_picker.retrieve_current_date())
        last_history_response = reader.retrieve(history_id.previous)
        current_history_response = reader.retrieve(history_id)
        request = HistoryUpdateRequest(
            id_=history_id,
            recurrent_operations=current_history_response.recurrent_operations
            | last_history_response.recurrent_operations,
            operations=current_history_response.operations,
        )
        updater.update(request)
        self._refresh()
