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
from dataclasses import dataclass

from PySide6.QtWidgets import QWidget, QHBoxLayout, QTableWidget

from src.application.budget.history.creator import HistoryCreator
from src.application.budget.history.reader import HistoryReader
from src.application.budget.history.updater import HistoryUpdater


@dataclass(frozen=True)
class SavingAccount:
    id: TSavingAccountId
    name: str
    balance: BalanceReference


class SavingAccountControlWidget(QWidget):
    add_operation_clicked = Signal(SavingAccount)
    delete_selected_clicked = Signal()
    copy_operations_from_previous_month_clicked = Signal()

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

        self._copy_operations_from_previous_month = QPushButton("Copy from Previous Month")
        self.form.addRow(self._copy_operations_from_previous_month)

        self._connect_signals()

    def _connect_signals(self) -> None:
        self._submit_button.clicked.connect(self._on_add_operation_clicked)
        self._delete_button.clicked.connect(self._on_delete_selected_clicked)
        self._copy_operations_from_previous_month.clicked.connect(self.copy_operations_from_previous_month_clicked.emit)

    def _on_add_operation_clicked(self) -> None:
        name = self.label_input.text()
        age = self._amount_input.value()
        if name and age:
            self.add_operation_clicked.emit(RecurrentOperation(name, age) if name and age else None)

    def _on_delete_selected_clicked(self) -> None:
        self.delete_selected_clicked.emit()


class SavingAccountTableWidget(QTableWidget):
    operations_modified = Signal(set)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setColumnCount(2)
        self.setHorizontalHeaderLabels(["Label", "Amount"])
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)  # type: ignore
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)  # type: ignore
        self._delegate = RecurrentOperationTableItemDelegate()
        self.setItemDelegateForColumn(0, self._delegate)
        self.setItemDelegateForColumn(1, self._delegate)
        self.setItemDelegateForColumn(2, self._delegate)
        self.setItemDelegateForColumn(3, self._delegate)

        self._connect_signals()

    def _connect_signals(self) -> None:
        self._delegate.editor_closed.connect(lambda: self.operations_modified.emit(self.operations))


class SavingManagementWidget(QWidget):
    def __init__(
        self,
        history_creator: HistoryCreator,
        history_updater: HistoryUpdater,
        history_reader: HistoryReader,
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)  # type: ignore

        layout = QHBoxLayout(self)

        self._recurrent_operation_table = RecurrentOperationsTableWidget()
        layout.addWidget(self._recurrent_operation_table)

        self._recurrent_operation_input = RecurrentOperationControlWidget(self)
        layout.addWidget(self._recurrent_operation_input)

        self._connect_signals()

    def _connect_signals(self) -> None:
        pass

    def refresh(self) -> None:
        pass
        # self._recurrent_operations_widget.refresh(recurrent_operations)
        # self._operations_widget.refresh(operations)
