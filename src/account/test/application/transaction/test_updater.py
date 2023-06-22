import datetime

import pytest

from src.account.application.transaction.creator import TransactionCreationRequest, TransactionCreator
from src.account.application.transaction.repository import TransactionRepository, TransactionNotFound
from src.account.application.transaction.updater import TransactionUpdateRequest, TransactionUpdater
from src.account.domain.transaction import Transaction
from src.account.test.domain.mocks import MockTransactionId


@pytest.fixture
def transaction_update_request(transaction_creation_request: TransactionUpdateRequest):
    return TransactionUpdateRequest(
        id=transaction_creation_request.id,
        account_id=transaction_creation_request.account_id,
        amount=transaction_creation_request.amount + 10,
        date=datetime.date.today(),
        label=f"{transaction_creation_request.label}_updated",
    )


def test_update_transaction(
    transaction_creation_request: TransactionCreationRequest,
    transaction_update_request: TransactionUpdateRequest,
    transaction_repository: TransactionRepository,
):
    sample_transaction_creator = TransactionCreator(repository=transaction_repository)
    sample_transaction_updater = TransactionUpdater(repository=transaction_repository)
    sample_transaction_creator.create(transaction_creation_request)

    transaction = transaction_repository.retrieve(MockTransactionId("1"))

    reference_transaction = Transaction(
        transaction.id, transaction.account_id, transaction.date, transaction.label, transaction.amount
    )

    reference_transaction.rectify_amount(transaction_update_request.amount)
    reference_transaction.rectify_date(transaction_update_request.date)
    reference_transaction.modify_label(transaction_update_request.label)

    sample_transaction_updater.update(transaction_update_request)

    transaction = transaction_repository.retrieve(transaction.id)

    assert transaction.id == reference_transaction.id
    assert transaction.account_id == reference_transaction.account_id
    assert transaction.amount == reference_transaction.amount
    assert transaction.date == reference_transaction.date
    assert transaction.label == reference_transaction.label


def test_update_unexisting_transaction(
    transaction_update_request: TransactionUpdateRequest, transaction_repository: TransactionRepository
):
    sample_transaction_updater = TransactionUpdater(repository=transaction_repository)

    with pytest.raises(TransactionNotFound):
        sample_transaction_updater.update(transaction_update_request)
