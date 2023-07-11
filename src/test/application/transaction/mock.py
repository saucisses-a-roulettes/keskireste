import ppa

from src.application.transaction.repository import TransactionRepository
from src.domain.transaction import TransactionId
from src.shared.application.id import IdFactory
from src.shared.application.repository import EntityAlreadyExists, EntityNotFound
from src.test.domain.mocks import MockTransactionId


@ppa.in_memory_repository(
    entity_already_exists_exception=EntityAlreadyExists, entity_not_found_exception=EntityNotFound
)
class TransactionMockRepository(TransactionRepository):
    pass


class MockTransactionIdFactory(IdFactory[TransactionId]):
    def __init__(self) -> None:
        self._id_template = MockTransactionId("mock_id")

    def generate_id(self) -> MockTransactionId:
        return self.id_template

    @property
    def id_template(self) -> MockTransactionId:
        return self._id_template

    @id_template.setter
    def id_template(self, id_template: MockTransactionId) -> None:
        self._id_template = id_template
