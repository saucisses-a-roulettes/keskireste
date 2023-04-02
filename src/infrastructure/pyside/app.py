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

import sys
from dataclasses import dataclass
from typing import Self
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QMainWindow,
    QMenu,
    QFileDialog,
    QSizePolicy,
    QStackedWidget,
    QWidget,
)
from ofxparse import OfxParser
from src.application.budget.creator import BudgetCreator
from src.application.budget.history.updater import HistoryUpdateRequest, HistoryUpdater
from src.application.budget.reader import BudgetReader, BudgetResponse
from src.domain.history import Date, Operation
from src.infrastructure.budget.history.repository.json_ import HistoryJsonRepository
from src.infrastructure.budget.history.repository.model import HistoryId
from src.infrastructure.budget.repository.json_ import BudgetJsonRepository
from src.infrastructure.budget.repository.model import BudgetPath
from src.infrastructure.pyside.history.container import (
    HistoryWidget,
    NoHistorySelectedWidget,
    retrieve_or_create_history,
)


@dataclass
class BudgetModel:
    id: BudgetPath
    histories_ids: frozenset[HistoryId]

    @classmethod
    def from_application(cls, b: BudgetResponse) -> Self:
        return cls(id=BudgetPath(str(b.id)), histories_ids=b.histories_ids)


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
