import datetime
import sys
from collections.abc import Callable, Mapping
from dataclasses import dataclass
from typing import Self
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
    QLabel,
    QLineEdit,
    QMainWindow,
    QMenu,
    QFileDialog,
    QPushButton,
    QSizePolicy,
    QSpinBox,
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

    def set_date(self, date: Date) -> None:
        self.year_selector.setCurrentText(date.year)
        self.month_selector.setCurrentText(date.month)

    def retrieve_date(self) -> Date:
        return Date(int(self.year_selector.currentText()), self.MONTHS[self.month_selector.currentText()])


class NoHistorySelectedWidget(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.test = QLabel("Sélectionne un budget !", self)


class RecurrentOperationInputWidget(QWidget):
    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent)
        self.form = QFormLayout(self)
        self.label_input = QLineEdit(self)
        self.form.addRow("Name", self.label_input)

        self.amount_input = QDoubleSpinBox(self)
        self.amount_input.setMaximum(100000000)
        self.amount_input.setMinimum(-99999999)
        self.amount_input.setDecimals(2)
        self.amount_input.setSingleStep(0.01)
        self.form.addRow("Amount", self.amount_input)

        self.submit_button = QPushButton("Add Operation", self)
        self.submit_button.setDefault(True)
        self.form.addRow(self.submit_button)

        self.delete_button = QPushButton("Delete Selected", self)
        self.form.addRow(self.delete_button)

    def connect_submit(self, f: Callable) -> None:
        self.submit_button.clicked.connect(f)

    def connect_delete(self, f: Callable) -> None:
        self.delete_button.clicked.connect(f)

    def get_recurrent_operation(self) -> RecurrentOperation | None:
        name = self.label_input.text()
        age = self.amount_input.value()
        return RecurrentOperation(name, age) if name and age else None


class HistoryWidget(QWidget):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.budget_path: BudgetPath | None = None

        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        layout = QGridLayout(self)

        self.date_picker = DatePicker()
        self.date_picker.year_selector.currentTextChanged.connect(self._refresh_ui)
        self.date_picker.month_selector.currentTextChanged.connect(self._refresh_ui)
        layout.addWidget(self.date_picker, 0, 0)

        self.title = QLabel("", self)
        layout.addWidget(self.title, 1, 0)

        self.recurrent_operation_table = QTableWidget()
        self.recurrent_operation_table.setColumnCount(2)
        self.recurrent_operation_table.setHorizontalHeaderLabels(["Label", "Amount"])
        self.recurrent_operation_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.recurrent_operation_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.recurrent_operation_table.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.recurrent_operation_table.setSortingEnabled(True)
        self.recurrent_operation_table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout.addWidget(self.recurrent_operation_table, 2, 0)

        self.recurrent_operation_input_widget = RecurrentOperationInputWidget(self)
        self.recurrent_operation_input_widget.connect_submit(self._add_recurrent_operation)
        self.recurrent_operation_input_widget.connect_delete(self._delete_recurrent_operation)
        layout.addWidget(self.recurrent_operation_input_widget, 2, 1)

        self.operation_table = QTableWidget()
        self.operation_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.operation_table.setColumnCount(3)
        self.operation_table.setHorizontalHeaderLabels(["Day", "Label", "Amount"])
        self.operation_table.setSortingEnabled(True)
        self.operation_table.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout.addWidget(self.operation_table, 3, 0)

        self.balance = QLabel("", self)
        layout.addWidget(self.balance, 3, 1)

    def _refresh_ui(self) -> None:
        history_id = HistoryId(self.budget_path, self.date_picker.retrieve_date())
        history = retrieve_or_create_history(history_id)
        self.title.setText(str(history.date))
        self.recurrent_operation_table.setRowCount(0)
        for op in history.recurrent_operations:
            row_index = self.recurrent_operation_table.rowCount()
            self.recurrent_operation_table.insertRow(row_index)
            self.recurrent_operation_table.setItem(row_index, 0, QTableWidgetItem(op.name))
            self.recurrent_operation_table.setItem(row_index, 1, QTableWidgetItem(str(op.value)))
        self.operation_table.setRowCount(0)
        for op in history.operations:
            row_index = self.operation_table.rowCount()
            self.operation_table.insertRow(row_index)
            self.operation_table.setItem(row_index, 0, QTableWidgetItem(str(op.day)))
            self.operation_table.setItem(row_index, 1, QTableWidgetItem(op.name))
            self.operation_table.setItem(row_index, 2, QTableWidgetItem(str(op.value)))
        self.balance.setText(
            f"Balance: {sum(op.value for op in history.recurrent_operations) + sum(op.value for op in history.operations):.2f}"
        )

    def refresh_history(self, budget_path: BudgetPath) -> None:
        self.budget_path = budget_path
        self._refresh_ui()

    def _add_recurrent_operation(self) -> None:
        reader = HistoryReader(repository=HistoryJsonRepository())
        updater = HistoryUpdater(repository=HistoryJsonRepository())
        if op := self.recurrent_operation_input_widget.get_recurrent_operation():
            history_id = HistoryId(self.budget_path, self.date_picker.retrieve_date())
            history = reader.retrieve(history_id)
            request = HistoryUpdateRequest(
                id_=history_id,
                recurrent_operations=history.recurrent_operations
                | {
                    op,
                },
                operations=history.operations,
            )
            updater.update(request)
            self._refresh_ui()

    def _delete_recurrent_operation(self) -> None:
        reader = HistoryReader(repository=HistoryJsonRepository())
        updater = HistoryUpdater(repository=HistoryJsonRepository())
        if selected_rows := {index.row() for index in self.recurrent_operation_table.selectionModel().selectedRows()}:
            history_id = HistoryId(self.budget_path, self.date_picker.retrieve_date())
            history_response = reader.retrieve(history_id)

            selected_recurrent_operations: set[RecurrentOperation] = set()
            for r in selected_rows:
                name = self.recurrent_operation_table.item(r, 0).text()
                amount = float(self.recurrent_operation_table.item(r, 1).text())
                selected_recurrent_operations.add(RecurrentOperation(name, amount))

            request = HistoryUpdateRequest(
                id_=history_id,
                recurrent_operations=history_response.recurrent_operations - selected_recurrent_operations,
                operations=history_response.operations,
            )
            updater.update(request)
            self._refresh_ui()

    def set_history(self, history_id: HistoryId) -> None:
        self.date_picker.set_date(history_id.date)
        self._refresh_ui()


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

        self.budget_layout = QGridLayout(self.history_widget)

    def refresh_history(self, budget_path: BudgetPath) -> None:
        self.history_widget.refresh_history(budget_path)
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
            self.central_widget.refresh_history(self._budget.id)

    def open_budget(self):
        reader = BudgetReader(repository=BudgetJsonRepository())
        file_path, _ = QFileDialog.getOpenFileName(self, "Open a file", "", "Every files (*)")

        if file_path:
            self._budget = BudgetModel.from_application(reader.retrieve(BudgetPath(file_path)))
            self.central_widget.refresh_history(self._budget.id)

    def import_operations(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Operations File", "", "Tous les fichiers (*.ofx)")
        history_updater = HistoryUpdater(repository=HistoryJsonRepository())
        if file_path:
            with open(file_path, "rb") as f:
                ofx = OfxParser.parse(f)
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
            self.central_widget.refresh_history(self._budget.id)


if __name__ == "__main__":
    app = QApplication()
    with open("src/infrastructure/style.qss", "r") as f:
        _style = f.read()
        app.setStyleSheet(_style)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
