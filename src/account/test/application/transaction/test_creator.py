import pytest

from src.account.application.transaction.creator import TransactionCreationRequest, TransactionCreator
from src.account.application.transaction.repository import TransactionRepository, TransactionAlreadyExists
from src.account.test.domain.mocks import MockTransactionId


def test_create_transaction(
    transaction_creation_request: TransactionCreationRequest, transaction_repository: TransactionRepository
):
    sample_transaction_creator = TransactionCreator(repository=transaction_repository)

    sample_transaction_creator.create(transaction_creation_request)

    assert transaction_repository.retrieve(MockTransactionId("1"))


def test_create_transaction_already_exists(
    transaction_creation_request: TransactionCreationRequest, transaction_repository: TransactionRepository
):
    sample_transaction_creator = TransactionCreator(repository=transaction_repository)
    sample_transaction_creator.create(transaction_creation_request)

    with pytest.raises(TransactionAlreadyExists):
        sample_transaction_creator.create(transaction_creation_request)
