from dataclasses import dataclass
from src.application.budget.history.repository import HistoryRepository
from src.domain.entity import Id
from src.domain.history import Date, History as DHistory, History, Operation, RecurrentOperation


@dataclass(frozen=True)
class HistoryCreationRequest:
    id_: Id
    date: Date
    recurrent_operations: set[RecurrentOperation]
    operations: set[Operation]


class HistoryCreator:
    def __init__(self, repository: HistoryRepository) -> None:
        self._repository = repository

    def create(self, request: HistoryCreationRequest) -> None:
        self._repository.create(
            History(
                id_=request.id_,
                date=request.date,
                recurrent_operations=request.recurrent_operations,
                operations=request.operations,
            )
        )
