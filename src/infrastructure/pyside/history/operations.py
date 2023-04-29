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
from typing import cast

from PySide6.QtCore import Signal, Qt, QModelIndex, QPersistentModelIndex, QObject
from PySide6.QtGui import QColor, QPen
from PySide6.QtWidgets import (
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
    QLabel,
    QStyledItemDelegate,
)

from src.domain.budget.history import SavingTransactionAspects, LoanTransactionAspects


@dataclass(frozen=True)
class RecurrentOperation:
    name: str
    value: float

    def __hash__(self):
        return hash(self.name)

    def __eq__(self, other: object) -> bool:
        if isinstance(other, RecurrentOperation):
            return self.name == other.name
        return False


@dataclass(frozen=True)
class Operation:
    id: str
    day: int
    name: str
    amount: float
    transaction_aspects: SavingTransactionAspects | LoanTransactionAspects | None = None

    def __hash__(self) -> int:
        return hash(self.day)


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


class OperationTableItemDelegate(QStyledItemDelegate):
    def __init__(self, border_color: QColor | None = None, parent: QObject | None = None) -> None:
        super().__init__(parent)
        self._border_color = border_color

    editor_closed = Signal()

    def paint(self, painter, option, index: QModelIndex | QPersistentModelIndex):
        super().paint(painter, option, index)

        if self._border_color:
            pen = QPen(self._border_color, 1, Qt.SolidLine)
            painter.setPen(pen)
            painter.drawRect(option.rect)

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
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)  # type: ignore
        self.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)  # type: ignore
        self.horizontalHeader().setSectionResizeMode(2, QHeaderView.Interactive)  # type: ignore
        self._delegate = OperationTableItemDelegate()
        self._saving_operation_delegate = OperationTableItemDelegate(QColor(Qt.yellow))
        self.setItemDelegateForColumn(0, self._delegate)
        self.setItemDelegateForColumn(1, self._delegate)
        self.setItemDelegateForColumn(2, self._delegate)
        self.setItemDelegateForColumn(3, self._delegate)
        self._connect_signals()

    def _connect_signals(self) -> None:
        self._delegate.editor_closed.connect(lambda: self.operations_modified.emit(self.operations))

    @property
    def operations(self) -> frozenset[Operation]:
        return frozenset(
            Operation(
                id=self.item(row_index, 0).text(),
                day=int(self.item(row_index, 1).text()),
                name=self.item(row_index, 2).text(),
                amount=float(self.item(row_index, 3).text()),
            )
            for row_index in range(self.rowCount())
        )

    def refresh(self, operations: frozenset[Operation]) -> None:
        self.setSortingEnabled(False)
        self.setRowCount(0)
        for op in operations:
            row_index = self.rowCount()
            self.insertRow(row_index)
            self.setItem(row_index, 0, QTableWidgetItem(op.id))
            day = QTableWidgetItem()
            day.setData(Qt.DisplayRole, op.day)  # type: ignore
            self.setItem(row_index, 1, day)
            self.setItem(row_index, 2, QTableWidgetItem(op.name))
            value = QTableWidgetItem()
            value.setData(Qt.DisplayRole, op.amount)  # type: ignore
            self.setItem(row_index, 3, value)
            if isinstance(op.transaction_aspects, SavingTransactionAspects):
                self.setItemDelegateForRow(row_index, self._saving_operation_delegate)
            else:
                self.setItemDelegateForRow(row_index, self._delegate)
        self.setSortingEnabled(True)


class OperationsWidget(QWidget):
    operations_modified = Signal(set)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)  # type: ignore

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
        deleted_ids = {self._operation_table.item(row_index, 0).text() for row_index in indexes}
        self.operations_modified.emit(frozenset(op for op in self.operations if op.id not in deleted_ids))

    def refresh(self, operations: frozenset[Operation]) -> None:
        self._operation_table.refresh(operations)

    @property
    def operations(self) -> frozenset[Operation]:
        return self._operation_table.operations


class RecurrentOperationTableItemDelegate(QItemDelegate):
    editor_closed = Signal()

    def createEditor(self, parent, option, index):
        if index.column() in (0, 1):
            editor = cast(QLineEdit, super().createEditor(parent, option, index))
            editor.editingFinished.connect(self.editor_closed.emit)
            return editor
        return None


class RecurrentOperationsTableWidget(QTableWidget):
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

    @property
    def operations(self) -> set[RecurrentOperation]:
        return {
            RecurrentOperation(
                name=self.item(row_index, 0).text(),
                value=float(self.item(row_index, 1).text()),
            )
            for row_index in range(self.rowCount())
        }

    def refresh(self, operations: frozenset[RecurrentOperation]) -> None:
        self.setSortingEnabled(False)
        self.setRowCount(0)
        for op in operations:
            row_index = self.rowCount()
            self.insertRow(row_index)
            self.setItem(row_index, 0, QTableWidgetItem(op.name))
            value = QTableWidgetItem()
            value.setData(Qt.DisplayRole, op.value)  # type: ignore
            self.setItem(row_index, 1, value)
        self.setSortingEnabled(True)


class RecurrentOperationsWidget(QWidget):
    recurrent_operations_modified = Signal(set)
    copy_operations_from_previous_month_clicked = Signal()
    operations_modified = Signal(set)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)  # type: ignore

        layout = QHBoxLayout(self)

        self._recurrent_operation_table = RecurrentOperationsTableWidget()
        layout.addWidget(self._recurrent_operation_table)

        self._recurrent_operation_input = RecurrentOperationControlWidget(self)
        layout.addWidget(self._recurrent_operation_input)

        self._connect_signals()

    def _connect_signals(self) -> None:
        self._recurrent_operation_input.add_operation_clicked.connect(lambda op: self._on_add_operation_clicked(op))
        self._recurrent_operation_input.delete_selected_clicked.connect(self._on_delete_selected_clicked)
        self._recurrent_operation_input.copy_operations_from_previous_month_clicked.connect(
            self.copy_operations_from_previous_month_clicked.emit
        )
        self._recurrent_operation_table.operations_modified.connect(lambda ops: self.operations_modified.emit(ops))

    def _on_add_operation_clicked(self, new_operation: RecurrentOperation) -> None:
        self.recurrent_operations_modified.emit(self._recurrent_operation_table.operations | {new_operation})

    def _on_delete_selected_clicked(self) -> None:
        indexes = {index.row() for index in self._recurrent_operation_table.selectionModel().selectedRows()}
        deleted_operation_names: set[str] = {
            self._recurrent_operation_table.item(row_index, 0).text() for row_index in indexes
        }
        self.recurrent_operations_modified.emit(
            ro for ro in self._recurrent_operation_table.operations if ro.name not in deleted_operation_names
        )

    def refresh(self, recurrent_operations: frozenset[RecurrentOperation]) -> None:
        self._recurrent_operation_table.refresh(recurrent_operations)


class HistoryOperationsManagementWidget(QWidget):
    show_dashboard_button_clicked = Signal()

    recurrent_operations_modified = Signal(set)

    copy_operations_from_previous_month_clicked = Signal()
    operations_modified = Signal(set)

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)  # type: ignore

        layout = QVBoxLayout(self)

        self._show_dashboard_button = QPushButton("Show Dashboard", self)
        layout.addWidget(self._show_dashboard_button)

        self._recurrent_operations_label = QLabel("Recurrent Operations:")
        layout.addWidget(self._recurrent_operations_label)
        self._recurrent_operations_widget = RecurrentOperationsWidget()
        layout.addWidget(self._recurrent_operations_widget)

        self._operations_label = QLabel("Operations of the months:")
        layout.addWidget(self._operations_label)
        self._operations_widget = OperationsWidget()
        layout.addWidget(self._operations_widget)

        self._connect_signals()

    def _connect_signals(self) -> None:
        self._show_dashboard_button.clicked.connect(lambda: self.show_dashboard_button_clicked.emit())
        self._recurrent_operations_widget.recurrent_operations_modified.connect(
            lambda ops: self.recurrent_operations_modified.emit(ops)
        )
        self._recurrent_operations_widget.copy_operations_from_previous_month_clicked.connect(
            lambda: self.copy_operations_from_previous_month_clicked.emit()
        )
        self._recurrent_operations_widget.operations_modified.connect(
            lambda ops: self.recurrent_operations_modified.emit(ops)
        )
        self._operations_widget.operations_modified.connect(lambda ops: self.operations_modified.emit(ops))

    def refresh(self, recurrent_operations: frozenset[RecurrentOperation], operations: frozenset[Operation]) -> None:
        self._recurrent_operations_widget.refresh(recurrent_operations)
        self._operations_widget.refresh(operations)

    @property
    def operations(self) -> frozenset[Operation]:
        return self._operations_widget.operations
