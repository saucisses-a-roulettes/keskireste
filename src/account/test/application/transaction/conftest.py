from datetime import datetime

import pytest

from src.account.application.transaction.creator import TransactionCreationRequest
from src.account.test.application.transaction.mock import TransactionMockRepository
from src.account.test.domain.mocks import MockTransactionId, MockAccountId


@pytest.fixture
def transaction_repository():
    return TransactionMockRepository()


@pytest.fixture
def transaction_creation_request():
    return TransactionCreationRequest(
        id=MockTransactionId("1"), account_id=MockAccountId("1"), date=datetime.date, label="label", amount=1.0
    )
