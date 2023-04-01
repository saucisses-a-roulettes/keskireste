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
import sys
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Self
from PySide6.QtCore import QMetaObject, Signal
from PySide6.QtGui import QAction, QStandardItem, QStandardItemModel
from PySide6.QtWidgets import (
    QAbstractItemView,
    QApplication,
    QComboBox,
    QDoubleSpinBox,
    QFormLayout,
    QGridLayout,
    QHBoxLayout,
    QHeaderView,
    QItemDelegate,
    QLabel,
    QLineEdit,
    QMainWindow,
    QMenu,
    QFileDialog,
    QPushButton,
    QSizePolicy,
    QStackedWidget,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)
from ofxparse import OfxParser
from src.application.budget.creator import BudgetCreator
from src.application.budget.history.creator import HistoryCreationRequest, HistoryCreator
from src.application.budget.history.reader import HistoryReadResponse, HistoryReader
from src.application.budget.history.updater import HistoryUpdateRequest, HistoryUpdater
from src.application.budget.reader import BudgetReader, BudgetResponse
from src.application.exception import BadRequestException
from src.domain.history import Date, Operation, RecurrentOperation
from src.infrastructure.budget.history.repository.json_ import HistoryJsonRepository
from src.infrastructure.budget.history.repository.model import HistoryId
from src.infrastructure.budget.repository.json_ import BudgetJsonRepository
from src.infrastructure.budget.repository.model import BudgetPath


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


@dataclass
class BudgetModel:
    id: BudgetPath
    histories_ids: frozenset[HistoryId]

    @classmethod
    def from_application(cls, b: BudgetResponse) -> Self:
        return cls(id=BudgetPath(str(b.id)), histories_ids=b.histories_ids)


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


class RecurrentOperationInputWidget(QWidget):
    add_operation_clicked = Signal(RecurrentOperation)
    delete_selected_clicked = Signal()

    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent)
        self.form = QFormLayout(self)
        self.label_input = QLineEdit(self)
        self.form.addRow("Name", self.label_input)

        self._amount_input = QDoubleSpinBox(self)
        self._amount_input.setMaximum(100000000)
        self._amount_input.setMinimum(-99999999)
        self._amount_input.setDecimals(2)
        self._amount_input.setSingleStep(0.01)
        self.form.addRow("Amount", self._amount_input)

        self._submit_button = QPushButton("Add Operation", self)
        self._submit_button.setDefault(True)
        self.form.addRow(self._submit_button)

        self._delete_button = QPushButton("Delete Selected", self)
        self.form.addRow(self._delete_button)

        self._connect_signals()

    def _connect_signals(self) -> None:
        self._submit_button.clicked.connect(self._on_add_operation_clicked)
        self._delete_button.clicked.connect(self._on_delete_selected_clicked)

    def _on_add_operation_clicked(self) -> None:
        name = self.label_input.text()
        age = self._amount_input.value()
        if name and age:
            self.add_operation_clicked.emit(RecurrentOperation(name, age) if name and age else None)

    def _on_delete_selected_clicked(self) -> None:
        self.delete_selected_clicked.emit()


class OperationTableItemDelegate(QItemDelegate):
    def createEditor(self, parent, option, index):
        if index.column() in (2, 3):
            return super().createEditor(parent, option, index)
        return None


class OperationsTableWidget(QTableWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setColumnCount(4)
        self.setHorizontalHeaderLabels(["Id", "Day", "Label", "Amount"])
        self.setSortingEnabled(True)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.horizontalHeader().setSectionResizeMode(2, QHeaderView.Interactive)
        delegate = OperationTableItemDelegate()
        self.setItemDelegateForColumn(0, delegate)
        self.setItemDelegateForColumn(1, delegate)
        self.setItemDelegateForColumn(2, delegate)
        self.setItemDelegateForColumn(3, delegate)

    def refresh(self, operations: frozenset[Operation]) -> None:
        self.setRowCount(0)
        for op in operations:
            row_index = self.rowCount()
            self.insertRow(row_index)
            self.setItem(row_index, 0, QTableWidgetItem(op.id))
            self.setItem(row_index, 1, QTableWidgetItem(str(op.day)))
            self.setItem(row_index, 2, QTableWidgetItem(op.name))
            self.setItem(row_index, 3, QTableWidgetItem(str(op.value)))


class RecurrentOperationsTableWidget(QTableWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setColumnCount(2)
        self.setHorizontalHeaderLabels(["Label", "Amount"])
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.setSelectionBehavior(QTableWidget.SelectRows)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.setSortingEnabled(True)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setEditTriggers(QTableWidget.NoEditTriggers)

    def refresh(self, operations: frozenset[RecurrentOperation]) -> None:
        self.setRowCount(0)
        for op in operations:
            row_index = self.rowCount()
            self.insertRow(row_index)
            self.setItem(row_index, 0, QTableWidgetItem(op.name))
            self.setItem(row_index, 1, QTableWidgetItem(str(op.value)))


class RecurrentOperationsWidget(QWidget):
    add_operation_clicked = Signal(RecurrentOperation)
    delete_selected_operations_clicked = Signal(set)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        layout = QHBoxLayout(self)
        self._recurrent_operation_table = RecurrentOperationsTableWidget()
        layout.addWidget(self._recurrent_operation_table)

        self._recurrent_operation_input = RecurrentOperationInputWidget(self)
        layout.addWidget(self._recurrent_operation_input)

        self._connect_signals()

    def _connect_signals(self) -> None:
        self._recurrent_operation_input.add_operation_clicked.connect(lambda op: self.add_operation_clicked.emit(op))
        self._recurrent_operation_input.delete_selected_clicked.connect(self._on_delete_selected_clicked)

    def _on_delete_selected_clicked(self) -> None:
        indexes = {index.row() for index in self._recurrent_operation_table.selectionModel().selectedRows()}
        recurrent_operations = {
            RecurrentOperation(
                self._recurrent_operation_table.item(i, 0).text(),
                float(self._recurrent_operation_table.item(i, 1).text()),
            )
            for i in indexes
        }
        self.delete_selected_operations_clicked.emit(recurrent_operations)

    def refresh(self, recurrent_operations: frozenset[RecurrentOperation]) -> None:
        self._recurrent_operation_table.refresh(recurrent_operations)


class HistoryOperationsManagerWidget(QWidget):
    show_dashboard_button_clicked = Signal()
    add_recurrent_operations_clicked = Signal(RecurrentOperation)
    delete_selected_recurrent_operations_clicked = Signal(set)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        layout = QVBoxLayout(self)

        self._show_dashboard_button = QPushButton("Show Dashboard", self)
        layout.addWidget(self._show_dashboard_button)

        self._recurrent_operations = RecurrentOperationsWidget()
        layout.addWidget(self._recurrent_operations)

        self._operation_table = OperationsTableWidget()
        layout.addWidget(self._operation_table)

        self._connect_signals()

    def _connect_signals(self) -> None:
        self._show_dashboard_button.clicked.connect(lambda: self.show_dashboard_button_clicked.emit())
        self._recurrent_operations.add_operation_clicked.connect(
            lambda op: self.add_recurrent_operations_clicked.emit(op)
        )
        self._recurrent_operations.delete_selected_operations_clicked.connect(
            lambda ops: self.delete_selected_recurrent_operations_clicked.emit(ops)
        )

    def refresh(self, recurrent_operations: frozenset[RecurrentOperation], operations: frozenset[Operation]) -> None:
        self._recurrent_operations.refresh(recurrent_operations)
        self._operation_table.refresh(operations)


class HistoryDashboardWidget(QWidget):
    manage_operations_button_clicked = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        layout = QVBoxLayout(self)

        self._manage_operations_button = QPushButton("Manage Operations", self)
        layout.addWidget(self._manage_operations_button)

        self._balance = QLabel("", self)
        layout.addWidget(self._balance)
        self._connect_signals()

    def _connect_signals(self) -> None:
        self._manage_operations_button.clicked.connect(lambda: self.manage_operations_button_clicked.emit())

    def refresh(self, recurrent_operations: frozenset[RecurrentOperation], operations: frozenset[Operation]) -> None:
        self._balance.setText(
            f"Balance: {sum(op.value for op in recurrent_operations) + sum(op.value for op in operations):.2f}"
        )


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


class MainWidget(QWidget):
    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent)
        layout = QHBoxLayout(self)

        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.history_stacked_widget = QStackedWidget()
        layout.addWidget(self.history_stacked_widget)
        self.history_stacked_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.no_history_selected_widget = NoHistorySelectedWidget()
        self.history_stacked_widget.addWidget(self.no_history_selected_widget)
        self.history_widget = HistoryWidget()
        self.history_stacked_widget.addWidget(self.history_widget)

    def refresh(self, budget_path: BudgetPath) -> None:
        self.history_widget.refresh(budget_path)
        self.history_stacked_widget.setCurrentWidget(self.history_widget)


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("KeskiReste")

        self._budget: BudgetModel | None = None

        # Menu
        menu_bar = self.menuBar()
        file_menu = QMenu("Files", self)
        menu_bar.addMenu(file_menu)
        open_file_action = QAction("Open a file", self)
        open_file_action.triggered.connect(self.open_budget)
        file_menu.addAction(open_file_action)
        create_file_action = QAction("Create a file", self)
        create_file_action.triggered.connect(self.create_budget)
        file_menu.addAction(create_file_action)

        data_menu = QMenu("Data", self)
        menu_bar.addMenu(data_menu)
        import_operations_action = QAction("Import operations", self)
        import_operations_action.triggered.connect(self.import_operations)
        data_menu.addAction(import_operations_action)

        # Central
        self.central_widget = MainWidget(self)
        self.central_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setCentralWidget(self.central_widget)

    def create_budget(self):
        creator = BudgetCreator(repository=BudgetJsonRepository())
        reader = BudgetReader(repository=BudgetJsonRepository())
        file_path, _ = QFileDialog.getSaveFileName(self, "New file", "", "Every files (*)")

        if file_path:
            creator.create(BudgetPath(file_path))
            self._budget = BudgetModel.from_application(reader.retrieve(BudgetPath(file_path)))
            self.central_widget.refresh(self._budget.id)

    def open_budget(self):
        reader = BudgetReader(repository=BudgetJsonRepository())
        file_path, _ = QFileDialog.getOpenFileName(self, "Open a file", "", "Every files (*)")

        if file_path:
            self._budget = BudgetModel.from_application(reader.retrieve(BudgetPath(file_path)))
            self.central_widget.refresh(self._budget.id)

    def import_operations(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Operations File", "", "Tous les fichiers (*.ofx)")
        history_updater = HistoryUpdater(repository=HistoryJsonRepository())
        if file_path:
            with open(file_path, "rb") as _f:
                ofx = OfxParser.parse(_f)
            account = ofx.account
            operations: dict[Date, set[Operation]] = {}
            for t in account.statement.transactions:
                date = Date(t.date.year, t.date.month)
                operations[date] = operations.get(date, set()) | {
                    Operation(id=t.id, name=t.payee, value=float(t.amount), day=t.date.day),
                }
            for date, ops in operations.items():
                history_id = HistoryId(self._budget.id, date)
                history_response = retrieve_or_create_history(history_id)

                request = HistoryUpdateRequest(
                    id_=history_id,
                    recurrent_operations=history_response.recurrent_operations,
                    operations=history_response.operations | ops,
                )
                history_updater.update(request)
            self.central_widget.refresh(self._budget.id)


if __name__ == "__main__":
    app = QApplication()
    with open("src/infrastructure/style.qss", "r") as f:
        _style = f.read()
        app.setStyleSheet(_style)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
