import logging

import pytest
from unittest.mock import MagicMock
from app.service.dto import CreateTransactionDto
from app.persistent.entity import UserEntity, CategoryEntity
from app.service.transactions import TransactionService
from app.persistent.entity import  IncomeEntity, ExpenseEntity

logging.basicConfig(level=logging.INFO)


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


def test_get_by_id(service, mock_transaction_repo):
    mock_transaction_repo.find_by_id.return_value = IncomeEntity(
        amount=200,
        user_id=1
    )

    found_transaction = service.get_by_id(10)
    assert found_transaction['type'] == 'income'
    assert found_transaction['amount'] == 200
    assert found_transaction['user_id'] == 1
    mock_transaction_repo.find_by_id.assert_called_once_with(10)


def test_add_transaction(service, mock_user_repo, mock_category_repo):
    mock_user_repo.find_by_id.return_value = UserEntity(
        id=1,
        name='U1',
        password='1234',
        email='u1@gmail.com',
        role='admin',
        is_active=True
    )
    dto = CreateTransactionDto(amount=100, user_id=1, category_id=10)

    added_transaction = service.add_transaction(dto)
    assert added_transaction is not None
    assert added_transaction['amount'] == 100
    assert added_transaction['user_id'] == 1
    assert added_transaction['category_id'] == 10

    mock_user_repo.find_by_id.assert_called_once_with(1)
    mock_category_repo.find_by_id.assert_called_once_with(10)


def test_create_transaction(service, mock_category_repo):
    dto = CreateTransactionDto(amount=100, user_id=1, category_id=10)
    mock_category_repo.find_by_id.return_value = CategoryEntity(name='C1', type_='income')

    created_transaction = service.create_transaction(dto)
    assert created_transaction is not None
    assert isinstance(created_transaction, IncomeEntity)
    assert created_transaction.user_id == 1
    assert created_transaction.category_id == 10

    mock_category_repo.find_by_id.assert_called_once_with(dto.category_id)


def test_update_transaction(service, mock_transaction_repo):
    transaction = IncomeEntity(id=1, amount=100, user_id=5, category_id=10)
    mock_transaction_repo.find_by_id.return_value = transaction

    service.update_transaction_amount(transaction_id=1, new_amount=200)

    assert transaction.amount == 200
    assert transaction.id == 1
    assert transaction.user_id == 5
    assert transaction.category_id == 10
    mock_transaction_repo.find_by_id.assert_called_once_with(1)


def test_get_all_transactions_for_category(service, mock_category_repo):
    category = MagicMock(name='salary', type_='income')
    mock_category_repo.find_by_name.return_value = category
    category.income_transactions = [
        IncomeEntity(amount=10, user_id=1, category_id=10),
        IncomeEntity(amount=20, user_id=2, category_id=10),
        IncomeEntity(amount=30, user_id=3, category_id=10)
    ]

    transactions = service.get_all_transactions_for_category('salary')

    assert transactions is not None
    assert len(transactions) == 3
    assert transactions[0]['amount'] == 10
    assert transactions[1]['amount'] == 20
    assert transactions[2]['amount'] == 30
    mock_category_repo.find_by_name.assert_called_once_with('salary')


def test_get_expense_transactions_higher_than(service, mock_expense_repo):
    transactions = [ExpenseEntity(amount=10, user_id=1, category_id=2),
                    ExpenseEntity(amount=50, user_id=2, category_id=3),
                    ExpenseEntity(amount=150, user_id=3, category_id=4)]
    mock_expense_repo.find_higher_than.return_value = [transactions[1], transactions[2]]

    expected_amount = 30
    expected_transactions = service.get_transactions_higher_than(expected_amount=expected_amount,
                                                                 transaction_type='EXPENSE')
    assert expected_transactions is not None
    assert len(expected_transactions) == 2
    assert expected_transactions[0]['amount'] == 50
    assert expected_transactions[1]['amount'] == 150
    mock_expense_repo.find_higher_than.assert_called_once_with(expected_amount)
