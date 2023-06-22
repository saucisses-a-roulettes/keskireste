import ppa

from src.account.application.transaction.repository import TransactionRepository
from src.shared.application.repository import EntityAlreadyExists, EntityNotFound


@ppa.in_memory_repository(
    entity_already_exists_exception=EntityAlreadyExists, entity_not_found_exception=EntityNotFound
)
class TransactionMockRepository(TransactionRepository):
    pass
