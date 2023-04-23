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
from collections.abc import Mapping

from PySide6.QtCharts import QChart, QBarSet, QBarSeries, QChartView, QBarCategoryAxis, QValueAxis, QLineSeries
from PySide6.QtCore import Qt, QPoint, Signal
from PySide6.QtGui import QPainter, QStandardItemModel, QStandardItem
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QComboBox

from src.application.budget.history.reader import HistoryReader, HistoryReadResponse
from src.application.budget.reader import BudgetReader
from src.infrastructure.budget.repository.model import BudgetPath


class DatePicker(QWidget):
    date_changed = Signal()

    def __init__(self, year: int, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        layout = QHBoxLayout(self)
        self._year_selector = QComboBox(self)
        model = QStandardItemModel()
        current_year: int = datetime.datetime.now().year
        for i in range(10):
            model.appendRow(QStandardItem(str(current_year - i)))
        self._year_selector.setModel(model)
        layout.addWidget(self._year_selector)

        self._year_selector.setCurrentText(str(year))

        self._connect_signals()

    def _connect_signals(self) -> None:
        self._year_selector.currentTextChanged.connect(self._on_date_changed)

    def _on_date_changed(self) -> None:
        self.date_changed.emit()

    @property
    def current_year(self) -> int:
        return int(self._year_selector.currentText())


class BudgetChartView(QChartView):
    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        self._ui()

    def _ui(self) -> None:
        self._chart = QChart()
        self._bar_series = QBarSeries()
        self._chart.addSeries(self._bar_series)
        self._line_series = QLineSeries()
        self._line_series.setName("Economies")
        self._chart.addSeries(self._line_series)
        self._chart.setTitle("Balance")
        self._chart.setAnimationOptions(QChart.SeriesAnimations)  # type: ignore

        categories = [f"{m}" for m in range(1, 13)]
        self._axis_x = QBarCategoryAxis()
        self._axis_x.append(categories)
        self._axis_x.setRange("1", "12")
        self._chart.addAxis(self._axis_x, Qt.AlignBottom)  # type: ignore
        self._bar_series.attachAxis(self._axis_x)
        self._line_series.attachAxis(self._axis_x)

        self._axis_y = QValueAxis()
        self._axis_y.setTickCount(20)
        self._chart.addAxis(self._axis_y, Qt.AlignLeft)  # type: ignore
        self._bar_series.attachAxis(self._axis_y)
        self._line_series.attachAxis(self._axis_y)
        self._chart.legend().setVisible(True)
        self._chart.legend().setAlignment(Qt.AlignBottom)  # type: ignore

        self.setChart(self._chart)
        self.setRenderHint(QPainter.Antialiasing)  # type: ignore

    def refresh(self, year: int, histories: list[HistoryReadResponse]) -> None:
        self._bar_series.clear()

        month_history_mapping: Mapping[int, HistoryReadResponse | None] = {
            m: next((h for h in histories if h.date.year == year and h.date.month == m), None) for m in range(1, 13)
        }

        balance_data_set = QBarSet("Balance")
        balances = [h.balance if h else 0 for m, h in month_history_mapping.items()]
        balance_data_set.append(balances)

        self._bar_series.append(balance_data_set)

        self._line_series.clear()
        v: float = 0
        economies = []
        for i, b in enumerate(balances):
            v += b or 0
            economies.append(v)
            self._line_series.append(QPoint(i, int(v)))

        max_range = max(abs(v) for v in balances + economies)

        self._axis_y.setRange(-max_range, max_range)
        self._chart.update()


class BudgetDashboardWidget(QWidget):
    def __init__(
        self, year: int, budget_reader: BudgetReader, history_reader: HistoryReader, parent: QWidget | None = None
    ) -> None:
        super().__init__(parent)

        self._budget_path: BudgetPath | None = None
        self._budget_reader = budget_reader
        self._history_reader = history_reader

        self._ui(year)
        self._connect_signals()

    def _ui(self, year: int) -> None:
        layout = QVBoxLayout(self)

        self._date_picker = DatePicker(year)
        layout.addWidget(self._date_picker)

        self._chart_view = BudgetChartView()
        layout.addWidget(self._chart_view)

    def _connect_signals(self) -> None:
        self._date_picker.date_changed.connect(lambda: self.refresh(self._budget_path))

    def refresh(self, budget_path: BudgetPath) -> None:
        self._budget_path = budget_path
        histories = self._history_reader.list_by_budget(budget_path)
        self._chart_view.refresh(self._date_picker.current_year, histories)
