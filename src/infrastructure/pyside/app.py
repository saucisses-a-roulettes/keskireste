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
from dataclasses import dataclass
from typing import Self

from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QApplication,
    QHBoxLayout,
    QMainWindow,
    QMenu,
    QFileDialog,
    QStackedWidget,
    QWidget,
    QSizePolicy,
    QTabWidget,
)
from ofxparse import OfxParser  # type: ignore

from src.application.budget.creator import BudgetCreator
from src.application.budget.history.creator import HistoryCreator
from src.application.budget.history.reader import HistoryReader
from src.application.budget.history.updater import HistoryUpdater
from src.application.budget.reader import BudgetReader, BudgetResponse
from src.infrastructure.budget.history.repository.json_ import HistoryJsonRepository
from src.infrastructure.budget.history.repository.model import HistoryId
from src.infrastructure.budget.repository.json_ import BudgetJsonRepository
from src.infrastructure.budget.repository.model import BudgetPath
from src.infrastructure.pyside.budget.dashboard import BudgetDashboardWidget
from src.infrastructure.pyside.history.container import (
    HistoryWidget,
    NoBudgetSelectedWidget,
)
from src.infrastructure.pyside.saving.management import SavingManagementWidget


@dataclass
class BudgetModel:
    id: BudgetPath
    histories_ids: frozenset[HistoryId]

    @classmethod
    def from_application(cls, b: BudgetResponse) -> Self:
        return cls(id=BudgetPath(str(b.id)), histories_ids=b.histories_ids)


class MainWidget(QWidget):
    def __init__(
        self,
        budget_reader: BudgetReader,
        history_creator: HistoryCreator,
        history_reader: HistoryReader,
        history_updater: HistoryUpdater,
        parent: QWidget,
    ) -> None:
        super().__init__(parent)
        layout = QHBoxLayout(self)

        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)  # type: ignore
        self._stacked_widget = QStackedWidget()
        layout.addWidget(self._stacked_widget)
        self._stacked_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)  # type: ignore
        self._no_history_selected_widget = NoBudgetSelectedWidget()
        self._stacked_widget.addWidget(self._no_history_selected_widget)

        self._tab_widget = QTabWidget()
        self._stacked_widget.addWidget(self._tab_widget)

        self._budget_dashboard_widget = BudgetDashboardWidget(
            datetime.datetime.now().year, budget_reader, history_reader
        )
        self._tab_widget.addTab(self._budget_dashboard_widget, "Dashboard")
        self._history_widget = HistoryWidget(history_creator, history_reader, history_updater)
        self._tab_widget.addTab(self._history_widget, "History")
        self._saving_management_widget = SavingManagementWidget()
        self._tab_widget.addTab(self._saving_management_widget, "Saving")
        self._connect_signals()

    def _connect_signals(self) -> None:
        self._history_widget.history_changed.connect(lambda budget_path: self.refresh(budget_path))

    def import_operations_from_ofx(self, file_path: str) -> None:
        self._history_widget.import_operations_from_ofx(file_path)

    def refresh(self, budget_path: BudgetPath) -> None:
        self._history_widget.refresh(budget_path)
        self._budget_dashboard_widget.refresh(budget_path)
        self._stacked_widget.setCurrentWidget(self._tab_widget)


class MainWindow(QMainWindow):
    def __init__(
        self,
        budget_creator: BudgetCreator,
        budget_reader: BudgetReader,
        history_creator: HistoryCreator,
        history_reader: HistoryReader,
        history_updater: HistoryUpdater,
    ) -> None:
        super().__init__()

        self._budget_creator = budget_creator
        self._budget_reader = budget_reader
        self._history_creator = history_creator
        self._history_reader = history_reader
        self._history_updater = history_updater
        self._budget: BudgetModel | None = None

        self._ui()

    def _ui(self) -> None:
        self.setWindowTitle("KeskiReste")
        menu_bar = self.menuBar()
        file_menu = QMenu("Files", self)
        menu_bar.addMenu(file_menu)
        open_file_action = QAction("Open a file", self)
        open_file_action.triggered.connect(self._open_budget)
        file_menu.addAction(open_file_action)
        create_file_action = QAction("Create a file", self)
        create_file_action.triggered.connect(self._create_budget)
        file_menu.addAction(create_file_action)

        data_menu = QMenu("Data", self)
        menu_bar.addMenu(data_menu)
        import_operations_action = QAction("Import operations", self)
        import_operations_action.triggered.connect(self._import_operations)
        data_menu.addAction(import_operations_action)

        self.central_widget = MainWidget(
            self._budget_reader, self._history_creator, self._history_reader, self._history_updater, self
        )
        self.central_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)  # type: ignore
        self.setCentralWidget(self.central_widget)

    def _create_budget(self):
        file_path, _ = QFileDialog.getSaveFileName(self, "New file", "", "Every files (*)")

        if file_path:
            self._budget_creator.create(BudgetPath(file_path))
            self._budget = BudgetModel.from_application(self._budget_reader.retrieve(BudgetPath(file_path)))
            self.central_widget.refresh(self._budget.id)

    def _open_budget(self):
        reader = BudgetReader(repository=BudgetJsonRepository())
        file_path, _ = QFileDialog.getOpenFileName(self, "Open a file", "", "Every files (*)")

        if file_path:
            self._budget = BudgetModel.from_application(reader.retrieve(BudgetPath(file_path)))
            self.central_widget.refresh(self._budget.id)

    def _import_operations(self) -> None:
        file_path, _ = QFileDialog.getOpenFileName(self, "Operations File", "", "Tous les fichiers (*.ofx)")
        if file_path:
            self.central_widget.import_operations_from_ofx(file_path)


if __name__ == "__main__":
    app = QApplication()

    budget_repository = BudgetJsonRepository()

    window = MainWindow(
        BudgetCreator(budget_repository),
        BudgetReader(budget_repository),
        HistoryCreator(HistoryJsonRepository()),
        HistoryReader(HistoryJsonRepository()),
        HistoryUpdater(HistoryJsonRepository()),
    )
    window.show()
    sys.exit(app.exec())
