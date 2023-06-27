import pytest

from src.account.application.reccurring_transaction.creator import (
    RecurringTransactionCreationRequest,
    RecurringTransactionCreator,
)
from src.account.application.reccurring_transaction.repository import (
    RecurringTransactionRepository,
    RecurringTransactionNotFound,
)
from src.account.application.reccurring_transaction.updater import (
    RecurringTransactionUpdateRequest,
    RecurringTransactionUpdater,
)
from src.account.domain.recurring_transaction import (
    WeeklyFrequency,
    Day,
    RecurringTransactionName,
    RecurringTransaction,
)
from src.account.test.domain.mocks import RecurringTransactionMockId


@pytest.fixture
def recurring_transaction_update_request(recurring_transaction_creation_request: RecurringTransactionUpdateRequest):
    return RecurringTransactionUpdateRequest(
        id=recurring_transaction_creation_request.id,
        account_id=recurring_transaction_creation_request.account_id,
        name=RecurringTransactionName(f"{recurring_transaction_creation_request.name}_updated"),
        amount=recurring_transaction_creation_request.amount + 10,
        frequency=WeeklyFrequency(Day(1)),
    )


def test_update_recurring_transaction(
    recurring_transaction_creation_request: RecurringTransactionCreationRequest,
    recurring_transaction_update_request: RecurringTransactionUpdateRequest,
    recurring_transaction_repository: RecurringTransactionRepository,
):
    sample_recurring_transaction_creator = RecurringTransactionCreator(repository=recurring_transaction_repository)
    sample_recurring_transaction_updater = RecurringTransactionUpdater(repository=recurring_transaction_repository)
    sample_recurring_transaction_creator.create(recurring_transaction_creation_request)

    recurring_transaction = recurring_transaction_repository.retrieve(RecurringTransactionMockId("1"))

    reference_recurring_transaction = RecurringTransaction(
        recurring_transaction.id,
        recurring_transaction.account_id,
        recurring_transaction.name,
        recurring_transaction.amount,
        recurring_transaction.frequency,
    )

    reference_recurring_transaction.rename(recurring_transaction_update_request.name)
    reference_recurring_transaction.modify_amount(recurring_transaction_update_request.amount)
    reference_recurring_transaction.modify_frequency(recurring_transaction_update_request.frequency)

    sample_recurring_transaction_updater.update(recurring_transaction_update_request)

    recurring_transaction = recurring_transaction_repository.retrieve(recurring_transaction.id)

    assert recurring_transaction.id == reference_recurring_transaction.id
    assert recurring_transaction.account_id == reference_recurring_transaction.account_id
    assert recurring_transaction.name == reference_recurring_transaction.name
    assert recurring_transaction.amount == reference_recurring_transaction.amount
    assert recurring_transaction.frequency == reference_recurring_transaction.frequency


def test_update_unexisting_transaction(
    recurring_transaction_update_request: RecurringTransactionUpdateRequest,
    recurring_transaction_repository: RecurringTransactionRepository,
):
    sample_recurring_transaction_updater = RecurringTransactionUpdater(repository=recurring_transaction_repository)

    with pytest.raises(RecurringTransactionNotFound):
        sample_recurring_transaction_updater.update(recurring_transaction_update_request)
