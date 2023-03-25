from dataclasses import dataclass
from src.application.budget.history.repository import HistoryRepository
from src.application.exception import BadRequestException
from src.application.repository import CannotRetrieveEntity
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
        try:
            history = self._repository.retrieve(id_)
        except CannotRetrieveEntity as err:
            raise BadRequestException(f"History `{id_}` not found") from err

        return HistoryReadResponse(
            date=history.date,
            recurrent_operations=history.recurrent_operations,
            operations=history.operations,
        )
