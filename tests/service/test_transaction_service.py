import pytest
from unittest.mock import MagicMock
from app.service.dto import CreateTransactionDto, TransactionDto
from app.persistent.entity import UserEntity
from app.service.transactions import TransactionService
from app.persistent.entity import TransactionEntity, IncomeEntity, ExpenseEntity


@pytest.fixture
def mock_income_repo():
    return MagicMock()


@pytest.fixture
def mock_expense_repo():
    return MagicMock()


@pytest.fixture
def mock_transaction_repo():
    return MagicMock()


@pytest.fixture
def mock_user_repo():
    return MagicMock()


@pytest.fixture
def mock_category_repo():
    return MagicMock()


@pytest.fixture
def service(mock_income_repo, mock_expense_repo, mock_transaction_repo,
            mock_user_repo, mock_category_repo):
    return TransactionService(
        mock_income_repo,
        mock_expense_repo,
        mock_transaction_repo,
        mock_user_repo,
        mock_category_repo
    )


def test_get_by_id(mock_income_repo, mock_expense_repo, mock_transaction_repo,
                     mock_user_repo, mock_category_repo):
    mock_transaction_repo.find_by_id.return_value = IncomeEntity(
        amount=200,
        user_id=1
    )
    service = TransactionService(mock_income_repo, mock_expense_repo, mock_transaction_repo,
                                 mock_user_repo, mock_category_repo)
    found_transaction = service.get_by_id(10)
    assert isinstance(found_transaction, IncomeEntity)
    assert found_transaction.amount == 200
    assert found_transaction.user_id == 1
    mock_transaction_repo.find_by_id.assert_called_once_with(10)


def test_add_transaction(mock_income_repo, mock_expense_repo, mock_transaction_repo,
                         mock_user_repo, mock_category_repo):
    mock_user_repo.find_by_id.return_value = UserEntity(
        id=1,
        name='U1',
        password='1234',
        email='u1@gmail.com',
        role='admin',
        is_active=True
    )
    dto = CreateTransactionDto(amount=100, user_id=1, category_id=10)
    service = TransactionService(
        mock_income_repo,
        mock_expense_repo,
        mock_transaction_repo,
        mock_user_repo,
        mock_category_repo
    )
    added_transaction = service.add_transaction(dto)
    assert added_transaction is not None
    assert added_transaction['amount'] == 100
    assert added_transaction['user_id'] == 1
    assert added_transaction['category_id'] == 10

    mock_user_repo.find_by_id.assert_called_once_with(1)
    mock_category_repo.find_by_id.assert_called_once_with(10)
