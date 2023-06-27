import pytest

from src.account.application.reccurring_transaction.creator import RecurringTransactionCreationRequest
from src.account.domain.recurring_transaction import RecurringTransactionName, DailyFrequency
from src.account.infrastructure.containers.in_memory import InMemoryContainer
from src.account.test.domain.mocks import RecurringTransactionMockId, MockAccountId


@pytest.fixture
def recurring_transaction_repository(container: InMemoryContainer):
    return container.recurring_transaction_repository()


@pytest.fixture
def recurring_transaction_creation_request():
    return RecurringTransactionCreationRequest(
        id=RecurringTransactionMockId("1"),
        account_id=MockAccountId("1"),
        name=RecurringTransactionName("RecurringTransaction"),
        amount=1.0,
        frequency=DailyFrequency,
    )
