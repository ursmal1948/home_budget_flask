import datetime
from datetime import timedelta
import logging
from werkzeug.exceptions import NotFound
import pytest
from unittest.mock import MagicMock
from app.service.dto import CreateRecurringTransactionDto
from app.persistent.entity import IncomeCategoryEntity, Frequency

from app.service.recurring_transactions import RecurringTransactionsService
from app.persistent.entity import (
    IncomeEntity,
    ExpenseEntity,
    IncomeRecurringTransactionEntity,
    ExpenseRecurringTransactionEntity
)

logging.basicConfig(level=logging.INFO)


@pytest.fixture
def current_date():
    return datetime.date.today()


@pytest.fixture
def mock_income_recurring_transaction_repo():
    return MagicMock()


@pytest.fixture
def mock_expene_recurring_transaction_repo():
    return MagicMock()


@pytest.fixture
def mock_user_repo():
    return MagicMock()


@pytest.fixture
def mock_category_repo():
    return MagicMock()


@pytest.fixture
def mock_income_repo():
    return MagicMock()


@pytest.fixture
def mock_expense_repo():
    return MagicMock()


@pytest.fixture
def mock_recurring_transaction_repo():
    return MagicMock()


@pytest.fixture
def service(
        mock_income_recurring_transaction_repo,
        mock_expene_recurring_transaction_repo,
        mock_user_repo,
        mock_category_repo,
        mock_income_repo,
        mock_expense_repo,
        mock_recurring_transaction_repo):
    return RecurringTransactionsService(
        mock_income_recurring_transaction_repo,
        mock_expene_recurring_transaction_repo,
        mock_user_repo,
        mock_category_repo,
        mock_income_repo,
        mock_expense_repo,
        mock_recurring_transaction_repo
    )


@pytest.fixture
def example_income_recurring_entity():
    return IncomeRecurringTransactionEntity(
        id=10,
        amount=100,
        frequency=Frequency.MONTHLY,
        user_id=11,
        next_due_date=datetime.date(2022, 2, 12),
        category_id=1,
        type_='income'
    )


def test_add_recurring_transaction(service, mock_user_repo, mock_category_repo,
                                   mock_income_recurring_transaction_repo,
                                   current_date):
    user_mock = MagicMock(id=20, name='User 1')
    mock_user_repo.find_by_id.return_value = user_mock
    income_category = IncomeCategoryEntity(id=11,
                                           name='Category 1',
                                           type_='income')
    mock_category_repo.find_by_id.return_value = income_category

    dto = CreateRecurringTransactionDto(
        amount=200,
        frequency=Frequency.MONTHLY,
        next_due_date=current_date + timedelta(days=3),
        category_id=income_category.id,
        user_id=user_mock.id,
    )
    added_transaction = service.add_recurring_transaction(dto)

    assert added_transaction is not None
    assert 'id' in added_transaction
    assert added_transaction['amount'] == 200
    assert added_transaction['frequency'] == Frequency.MONTHLY.name
    assert added_transaction['user_id'] == 20
    mock_user_repo.find_by_id.assert_called_once_with(dto.user_id)
    mock_category_repo.find_by_id.assert_called_once_with(income_category.id)
    mock_income_recurring_transaction_repo.save_or_update.assert_called_once()


def test_get_by_id(mock_recurring_transaction_repo, service):
    income_recurring_trans = IncomeRecurringTransactionEntity(
        id=1,
        amount=20,
        frequency=Frequency.MONTHLY,
        user_id=1,
        next_due_date=datetime.date(2026, 12, 9),
        category_id=1,
        type_='income'
    )
    mock_recurring_transaction_repo.find_by_id.return_value = income_recurring_trans

    found_transaction = service.get_by_id(transaction_id=1)
    assert found_transaction is not None
    assert found_transaction['id'] == income_recurring_trans.id
    assert found_transaction['amount'] == income_recurring_trans.amount
    assert found_transaction['type'] == 'income'
    mock_recurring_transaction_repo.find_by_id.assert_called_once_with(1)


def test_get_by_id_transaction_not_found(service, mock_recurring_transaction_repo):
    mock_recurring_transaction_repo.find_by_id.return_value = None

    with pytest.raises(NotFound) as err:
        service.get_by_id(transaction_id=1)
    assert 'Recurring transaction not found' in str(err.value)
    mock_recurring_transaction_repo.find_by_id.assert_called_once_with(1)


def test_create_income_transaction(service, mock_income_repo, mock_income_recurring_transaction_repo, current_date):
    recurring_transaction = IncomeRecurringTransactionEntity(
        id=1,
        amount=20,
        frequency=Frequency.DAILY,
        user_id=1,
        next_due_date=current_date,
        category_id=1,
        type_='income'
    )
    income_transaction = IncomeEntity(
        amount=recurring_transaction.amount,
        user_id=recurring_transaction.user_id,
        category_id=recurring_transaction.category_id,
    )
    service.create_income_transaction(recurring_transaction)

    assert recurring_transaction.next_due_date == current_date + timedelta(days=1)
    assert recurring_transaction.amount == income_transaction.amount
    mock_income_repo.save_or_update.assert_called_once()
    mock_income_recurring_transaction_repo.save_or_update.assert_called_once_with(recurring_transaction)


def test_create_expense_transaction(service, mock_expense_repo, mock_expene_recurring_transaction_repo, current_date):
    recurring_transaction = ExpenseRecurringTransactionEntity(
        id=2,
        amount=30,
        frequency=Frequency.WEEKLY,
        user_id=1,
        next_due_date=current_date,
        category_id=2,
        type_='expense'
    )
    expense_transaction = ExpenseEntity(
        amount=recurring_transaction.amount,
        user_id=recurring_transaction.user_id,
        category_id=recurring_transaction.category_id
    )
    service.create_expense_transaction(recurring_transaction)

    assert recurring_transaction.next_due_date == current_date + timedelta(weeks=1)
    assert recurring_transaction.amount == expense_transaction.amount
    mock_expense_repo.save_or_update.assert_called_once()
    mock_expene_recurring_transaction_repo.save_or_update.assert_called_once_with(recurring_transaction)


def test_update_recurring_transaction(service, mock_recurring_transaction_repo, current_date):
    transaction = ExpenseRecurringTransactionEntity(
        id=3,
        amount=40,
        frequency=Frequency.WEEKLY,
        user_id=2,
        next_due_date=current_date,
        category_id=3,
        type_='expense'
    )

    mock_recurring_transaction_repo.find_by_id.return_value = transaction
    next_due_date = datetime.date(2026, 10, 15)
    service.update_recurring_transaction(
        transaction_id=3,
        amount=100,
        frequency=Frequency.MONTHLY,
        next_due_date=next_due_date
    )
    assert transaction.frequency == Frequency.MONTHLY
    assert transaction.next_due_date != current_date and transaction.next_due_date == next_due_date
    assert transaction.amount == 100
    mock_recurring_transaction_repo.find_by_id.assert_called_once_with(3)


def test_validate_date_of_transaction_next_due_date_in_past(service, mock_recurring_transaction_repo,
                                                            example_income_recurring_entity,
                                                            current_date):
    result = service._validate_date_of_transaction(example_income_recurring_entity, current_date)
    assert result is None
    mock_recurring_transaction_repo.delete_by_id.assert_called_once_with(example_income_recurring_entity.id)


def test_validate_date_of_transaction_next_due_date_in_future(service,
                                                              example_income_recurring_entity, current_date
                                                              ):
    example_income_recurring_entity.next_due_date = current_date + timedelta(days=2)
    result = service._validate_date_of_transaction(example_income_recurring_entity, current_date)
    assert result is None


def validate_date_of_transaction_next_due_date_equals_current(service,
                                                              example_income_recurring_entity,
                                                              current_date):
    example_income_recurring_entity.next_due_date = current_date
    transaction = service._validate_date_of_transaction(example_income_recurring_entity, current_date)
    assert transaction is None
    assert isinstance(transaction, IncomeRecurringTransactionEntity)
