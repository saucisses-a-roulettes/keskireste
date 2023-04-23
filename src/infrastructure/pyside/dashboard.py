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
from PySide6.QtCore import Qt, QPoint
from PySide6.QtGui import QPainter
from PySide6.QtWidgets import QWidget, QVBoxLayout

from src.application.budget.history.reader import HistoryReader, HistoryReadResponse
from src.application.budget.reader import BudgetReader
from src.domain.history import History
from src.infrastructure.budget.repository.model import BudgetPath


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
        self._chart.addAxis(self._axis_x, Qt.AlignBottom)
        self._bar_series.attachAxis(self._axis_x)
        self._line_series.attachAxis(self._axis_x)

        self._axis_y = QValueAxis()
        self._axis_y.setTickCount(20)
        self._chart.addAxis(self._axis_y, Qt.AlignLeft)
        self._bar_series.attachAxis(self._axis_y)
        self._line_series.attachAxis(self._axis_y)
        self._chart.legend().setVisible(True)
        self._chart.legend().setAlignment(Qt.AlignBottom)

        self.setChart(self._chart)
        self.setRenderHint(QPainter.Antialiasing)

    def refresh(self, year: int, histories: list[HistoryReadResponse]) -> None:
        self._bar_series.clear()

        month_history_mapping: Mapping[int, History | None] = {
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

        self._axis_y.setRange(min(balances + economies), max(balances + economies))
        self._chart.update()


class BudgetDashboardWidget(QWidget):
    def __init__(
        self, budget_reader: BudgetReader, history_reader: HistoryReader, parent: QWidget | None = None
    ) -> None:
        super().__init__(parent)

        self._budget_reader = budget_reader
        self._history_reader = history_reader

        self._ui()

    def _ui(self) -> None:
        layout = QVBoxLayout(self)

        self._chart_view = BudgetChartView()
        layout.addWidget(self._chart_view)

    def refresh(self, budget_path: BudgetPath) -> None:
        histories = self._history_reader.list_by_budget(budget_path)
        self._chart_view.refresh(datetime.datetime.now().year, histories)
