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

from PySide6.QtCore import Signal
from PySide6.QtWidgets import QLabel, QPushButton, QSizePolicy, QVBoxLayout, QWidget

from src.application.budget.history.reader import OperationReadResponse
from src.domain.budget.history import RecurrentOperation


class HistoryDashboardWidget(QWidget):
    manage_operations_button_clicked = Signal()

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)  # type: ignore

        layout = QVBoxLayout(self)

        self._manage_operations_button = QPushButton("Manage Operations", self)
        layout.addWidget(self._manage_operations_button)

        self._balance = QLabel("", self)
        layout.addWidget(self._balance)
        self._connect_signals()

    def _connect_signals(self) -> None:
        self._manage_operations_button.clicked.connect(lambda: self.manage_operations_button_clicked.emit())

    def refresh(
        self, recurrent_operations: frozenset[RecurrentOperation], operations: frozenset[OperationReadResponse]
    ) -> None:
        self._balance.setText(
            f"Balance: {sum(op.value for op in recurrent_operations) + sum(op.amount for op in operations):.2f}"
        )
