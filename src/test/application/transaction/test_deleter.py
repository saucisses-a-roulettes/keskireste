import pytest
from pytest_mock import MockFixture

from src.application.transaction.creator import TransactionCreationRequest, TransactionCreator
from src.application.transaction.deleter import TransactionDeletionRequest, TransactionDeleter
from src.application.transaction.repository import TransactionRepository, TransactionNotFound


def test_delete_transaction(
    mocker: MockFixture,
    transaction_creation_request: TransactionCreationRequest,
    transaction_deletion_request: TransactionDeletionRequest,
    transaction_repository: TransactionRepository,
):
    spy = mocker.spy(transaction_repository, "delete")
    sample_transaction_creator = TransactionCreator(repository=transaction_repository)
    sample_transaction_deleter = TransactionDeleter(repository=transaction_repository)
    sample_transaction_creator.create(transaction_creation_request)

    sample_transaction_deleter.delete(transaction_deletion_request)

    spy.assert_called_once_with(transaction_deletion_request.id)


def test_delete_unexisting_transaction(
    transaction_deletion_request: TransactionDeletionRequest, transaction_repository: TransactionRepository
):
    sample_transaction_deleter = TransactionDeleter(repository=transaction_repository)

    with pytest.raises(TransactionNotFound):
        sample_transaction_deleter.delete(transaction_deletion_request)
