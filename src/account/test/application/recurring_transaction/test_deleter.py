import pytest
from pytest_mock import MockFixture

from src.account.application.reccurring_transaction.creator import (
    RecurringTransactionCreationRequest,
    RecurringTransactionCreator,
)
from src.account.application.reccurring_transaction.deleter import (
    RecurringTransactionDeletionRequest,
    RecurringTransactionDeleter,
)
from src.account.application.reccurring_transaction.repository import (
    RecurringTransactionRepository,
    RecurringTransactionNotFound,
)


def test_delete_recurring_transaction(
    mocker: MockFixture,
    recurring_transaction_creation_request: RecurringTransactionCreationRequest,
    recurring_transaction_deletion_request: RecurringTransactionDeletionRequest,
    recurring_transaction_repository: RecurringTransactionRepository,
):
    spy = mocker.spy(recurring_transaction_repository, "delete")
    sample_recurring_transaction_creator = RecurringTransactionCreator(repository=recurring_transaction_repository)
    sample_recurring_transaction_deleter = RecurringTransactionDeleter(repository=recurring_transaction_repository)
    sample_recurring_transaction_creator.create(recurring_transaction_creation_request)

    sample_recurring_transaction_deleter.delete(recurring_transaction_deletion_request)

    spy.assert_called_once_with(recurring_transaction_deletion_request.id)


def test_delete_unexisting_recurring_transaction(
    recurring_transaction_deletion_request: RecurringTransactionDeletionRequest,
    recurring_transaction_repository: RecurringTransactionRepository,
):
    sample_recurring_transaction_deleter = RecurringTransactionDeleter(repository=recurring_transaction_repository)

    with pytest.raises(RecurringTransactionNotFound):
        sample_recurring_transaction_deleter.delete(recurring_transaction_deletion_request)
