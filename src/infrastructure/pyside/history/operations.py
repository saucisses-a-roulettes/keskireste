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
from typing import cast

from PySide6.QtCore import QModelIndex, Signal, Qt
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


class RecurrentOperationControlWidget(QWidget):
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


class OperationControlWidget(QWidget):
    delete_selected_clicked = Signal()

    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent)
        self.form = QFormLayout(self)

        self._delete_button = QPushButton("Delete Selected", self)
        self.form.addRow(self._delete_button)

        self._connect_signals()

    def _connect_signals(self) -> None:
        self._delete_button.clicked.connect(self._on_delete_selected_clicked)

    def _on_delete_selected_clicked(self) -> None:
        self.delete_selected_clicked.emit()


class OperationTableItemDelegate(QItemDelegate):
    editor_closed = Signal()

    def createEditor(self, parent, option, index):
        if index.column() in (2, 3):
            editor = cast(QLineEdit, super().createEditor(parent, option, index))
            editor.editingFinished.connect(self.editor_closed.emit)
            return editor
        return None


class OperationsTableWidget(QTableWidget):
    operations_modified = Signal(set)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setColumnCount(4)
        self.setHorizontalHeaderLabels(["Id", "Day", "Label", "Amount"])
        self.setSortingEnabled(True)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.horizontalHeader().setSectionResizeMode(2, QHeaderView.Interactive)
        self._delegate = OperationTableItemDelegate()
        self.setItemDelegateForColumn(0, self._delegate)
        self.setItemDelegateForColumn(1, self._delegate)
        self.setItemDelegateForColumn(2, self._delegate)
        self.setItemDelegateForColumn(3, self._delegate)
        self._connect_signals()

    def _connect_signals(self) -> None:
        self._delegate.editor_closed.connect(lambda: self.operations_modified.emit(self.operations))

    @property
    def operations(self) -> set[Operation]:
        return {
            Operation(
                id=self.item(row_index, 0).text(),
                day=int(self.item(row_index, 1).text()),
                name=self.item(row_index, 2).text(),
                value=float(self.item(row_index, 3).text()),
            )
            for row_index in range(self.rowCount())
        }

    def refresh(self, operations: frozenset[Operation]) -> None:
        self.setSortingEnabled(False)
        self.setRowCount(0)
        for op in operations:
            row_index = self.rowCount()
            self.insertRow(row_index)
            self.setItem(row_index, 0, QTableWidgetItem(op.id))
            day = QTableWidgetItem()
            day.setData(Qt.DisplayRole, op.day)
            self.setItem(row_index, 1, day)
            self.setItem(row_index, 2, QTableWidgetItem(op.name))
            value = QTableWidgetItem()
            value.setData(Qt.DisplayRole, op.value)
            self.setItem(row_index, 3, value)
        self.setSortingEnabled(True)


class OperationsWidget(QWidget):
    operations_deleted = Signal(set)
    operations_modified = Signal(set)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        layout = QHBoxLayout(self)
        self._operation_table = OperationsTableWidget()
        layout.addWidget(self._operation_table)

        self._operations_control = OperationControlWidget(self)
        layout.addWidget(self._operations_control)

        self._connect_signals()

    def _connect_signals(self) -> None:
        self._operations_control.delete_selected_clicked.connect(self._on_delete_selected_clicked)
        self._operation_table.operations_modified.connect(lambda ops: self.operations_modified.emit(ops))

    def _on_delete_selected_clicked(self) -> None:
        indexes = {index.row() for index in self._operation_table.selectionModel().selectedRows()}
        operations = {
            Operation(
                id=self._operation_table.item(row_index, 0).text(),
                day=int(self._operation_table.item(row_index, 1).text()),
                name=self._operation_table.item(row_index, 2).text(),
                value=float(self._operation_table.item(row_index, 3).text()),
            )
            for row_index in indexes
        }
        self.operations_deleted.emit(operations)

    def refresh(self, operations: frozenset[Operation]) -> None:
        self._operation_table.refresh(operations)


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
            value = QTableWidgetItem()
            value.setData(Qt.DisplayRole, op.value)
            self.setItem(row_index, 1, value)


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

        self._recurrent_operation_input = RecurrentOperationControlWidget(self)
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
    operations_modified = Signal(set)
    operations_deleted = Signal(set)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        layout = QVBoxLayout(self)

        self._show_dashboard_button = QPushButton("Show Dashboard", self)
        layout.addWidget(self._show_dashboard_button)

        self._recurrent_operations = RecurrentOperationsWidget()
        layout.addWidget(self._recurrent_operations)

        self._operations = OperationsWidget()
        layout.addWidget(self._operations)

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
        self._operations.operations_modified.connect(lambda ops: self.operations_modified.emit(ops))
        self._operations.operations_deleted.connect(lambda ops: self.operations_deleted.emit(ops))

    def refresh(self, recurrent_operations: frozenset[RecurrentOperation], operations: frozenset[Operation]) -> None:
        self._recurrent_operations.refresh(recurrent_operations)
        self._operations.refresh(operations)
