import pytest

from src.application.transaction.creator import TransactionCreationRequest, TransactionCreator
from src.application.transaction.repository import TransactionRepository, TransactionAlreadyExists
from src.test.application.transaction.mock import MockTransactionIdFactory
from src.test.domain.mocks import MockTransactionId


def test_create_transaction(
    transaction_creation_request: TransactionCreationRequest,
    transaction_repository: TransactionRepository,
    transaction_id_factory: MockTransactionIdFactory,
):
    sample_transaction_creator = TransactionCreator(
        repository=transaction_repository, id_factory=transaction_id_factory
    )

    sample_transaction_creator.create(transaction_creation_request)

    assert transaction_repository.retrieve(transaction_id_factory.id_template)


def test_create_transaction_already_exists(
    transaction_creation_request: TransactionCreationRequest,
    transaction_repository: TransactionRepository,
    transaction_id_factory: MockTransactionIdFactory,
):
    sample_transaction_creator = TransactionCreator(
        repository=transaction_repository, id_factory=transaction_id_factory
    )
    sample_transaction_creator.create(transaction_creation_request)

    with pytest.raises(TransactionAlreadyExists):
        sample_transaction_creator.create(transaction_creation_request)
