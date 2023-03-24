import datetime
import sys
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Self
from PySide6.QtGui import QAction, QStandardItem, QStandardItemModel
from PySide6.QtWidgets import (
    QApplication,
    QComboBox,
    QLabel,
    QMainWindow,
    QMenu,
    QFileDialog,
    QVBoxLayout,
    QWidget,
)
from src.application.budget.creator import BudgetCreator
from src.application.budget.history.creator import HistoryCreationRequest, HistoryCreator
from src.application.budget.history.reader import HistoryReader
from src.application.budget.reader import BudgetReader, BudgetResponse
from src.domain.entity import Id
from src.domain.history import Date
from src.infrastructure.budget.history.repository.pickle import HistoryId, HistoryPickleRepository
from src.infrastructure.budget.repository.model import BudgetPath
from src.infrastructure.budget.repository.pickle import BudgetPickleRepository


@dataclass
class BudgetModel:
    id: BudgetPath
    histories_ids: frozenset[HistoryId]


class MainWindow(QMainWindow):
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

    def __init__(self):
        super().__init__()

        self.setWindowTitle("KeskiReste")

        self._budget: BudgetModel | None = None

        # Menu
        menu_bar = self.menuBar()
        file_menu = QMenu("Fichier", self)
        menu_bar.addMenu(file_menu)
        open_file_action = QAction("Ouvrir un fichier", self)
        open_file_action.triggered.connect(self.open_budget)
        file_menu.addAction(open_file_action)
        create_file_action = QAction("Créer un fichier", self)
        create_file_action.triggered.connect(self.create_budget)
        file_menu.addAction(create_file_action)

        # Central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)

        self.year_selector = QComboBox()
        model = QStandardItemModel()
        current_year: int = datetime.datetime.now().year
        for i in range(10):
            model.appendRow(QStandardItem(str(current_year - i)))
        self.year_selector.setModel(model)
        layout.addWidget(self.year_selector)
        self.year_selector.currentTextChanged.connect(self._load_history)

        self.month_selector = QComboBox()
        model = QStandardItemModel()
        for month in self.MONTHS:
            model.appendRow(QStandardItem(month))
        self.month_selector.setModel(model)
        current_month = datetime.datetime.now().month
        self.month_selector.setCurrentText(next(key for key, value in self.MONTHS.items() if value == current_month))
        layout.addWidget(self.month_selector)
        self.month_selector.currentTextChanged.connect(self._load_history)

        self.test = QLabel("Sélectionne un budget !")
        layout.addWidget(self.test)

    def _load_budget(self) -> None:
        self.test.setText(str(self._budget.id))

    def _load_history(self) -> None:
        reader = HistoryReader(repository=HistoryPickleRepository())
        creator = HistoryCreator(repository=HistoryPickleRepository())
        year = int(self.year_selector.currentText())
        month = self.MONTHS[self.month_selector.currentText()]
        try:
            history_id: HistoryId = next(
                h for h in self._budget.histories_ids if h.date.year == year and h.date.month == month
            )
        except StopIteration:
            history_id = HistoryId(self._budget.id, Date(year, month))
            creator.create(
                HistoryCreationRequest(
                    id_=history_id, date=Date(year, month), recurrent_operations=set(), operations=set()
                )
            )
        history = reader.retrieve(history_id)
        self.test.setText(f"{history.date.year}{history.date.month}")

    def create_budget(self):
        creator = BudgetCreator(repository=BudgetPickleRepository())
        reader = BudgetReader(repository=BudgetPickleRepository())
        # Demander un nom de fichier à l'utilisateur
        file_path, _ = QFileDialog.getSaveFileName(self, "Nouveau fichier", "", "Tous les fichiers (*)")

        if file_path:
            creator.create(BudgetPath(file_path))
            self._budget = BudgetModel.from_application(reader.read(BudgetPath(file_path)))
            self._load_budget()

    def open_budget(self):
        reader = BudgetReader(repository=BudgetPickleRepository())
        # Ouvrir une boîte de dialogue pour sélectionner un fichier
        file_path, _ = QFileDialog.getOpenFileName(self, "Ouvrir un fichier", "", "Tous les fichiers (*)")

        if file_path:
            self._budget = reader.read(BudgetPath(file_path))
            self._load_budget()


if __name__ == "__main__":
    app = QApplication()
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
