from dataclasses import dataclass
from src.application.budget.history.repository import HistoryRepository
from src.domain.entity import Id
from src.domain.history import Date, History as DHistory, History, Operation, RecurrentOperation


@dataclass(frozen=True)
class HistoryReadResponse:
    date: Date
    recurrent_operations: set[RecurrentOperation]
    operations: set[Operation]


class HistoryReader:
    def __init__(self, repository: HistoryRepository) -> None:
        self._repository = repository

    def retrieve(self, id_: Id) -> HistoryReadResponse:
        history = self._repository.retrieve(id_)

        return HistoryReadResponse(
            date=history.date,
            recurrent_operations=history.recurrent_operations,
            operations=history.operations,
        )
