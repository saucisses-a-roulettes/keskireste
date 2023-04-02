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
from PySide6.QtWidgets import (
    QAbstractItemView,
    QDoubleSpinBox,
    QFormLayout,
    QHBoxLayout,
    QHeaderView,
    QItemDelegate,
    QLineEdit,
    QPushButton,
    QSizePolicy,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)
from src.domain.history import Operation, RecurrentOperation


class RecurrentOperationInputWidget(QWidget):
    add_operation_clicked = Signal(RecurrentOperation)
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
    copy_operations_from_previous_month_clicked = Signal()

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
        self._recurrent_operation_input.copy_operations_from_previous_month_clicked.connect(
            self.copy_operations_from_previous_month_clicked.emit
        )

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
    copy_operations_from_previous_month_clicked = Signal()

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
        self._recurrent_operations.copy_operations_from_previous_month_clicked.connect(
            lambda: self.copy_operations_from_previous_month_clicked.emit()
        )

    def refresh(self, recurrent_operations: frozenset[RecurrentOperation], operations: frozenset[Operation]) -> None:
        self._recurrent_operations.refresh(recurrent_operations)
        self._operation_table.refresh(operations)
