import logging

import pytest
from unittest.mock import MagicMock
from app.service.dto import CreateCategorizedBudgetEntryDto
from app.persistent.entity import ExpenseCategoryEntity
from app.service.budget_planning import BudgetPlanningService

logging.basicConfig(level=logging.INFO)


@pytest.fixture
def user_mock_repo():
    return MagicMock()


@pytest.fixture
def category_mock_repo():
    return MagicMock()


@pytest.fixture
def service(user_mock_repo, category_mock_repo):
    return BudgetPlanningService(
        user_repository=user_mock_repo,
        category_repository=category_mock_repo
    )


def test_calculate_actual_spending_for_category(service, user_mock_repo, category_mock_repo):
    category = ExpenseCategoryEntity(id=1, name='Rent', type_='expense')
    category_mock_repo.find_by_id.return_value = category
    user_mock_repo.calculate_total_expenses.return_value = 500
    user_actual_spendings_for_category = service._calculate_actual_spending_for_category(
        user_id=1,
        category_id=category.id
    )
    assert user_actual_spendings_for_category is not None
    assert user_actual_spendings_for_category == 500
    category_mock_repo.find_by_id.assert_called_once_with(1)
    user_mock_repo.calculate_total_expenses.assert_called_once_with(1, 1)


def test_calculate_planned_spending_for_user_by_category(service, user_mock_repo, category_mock_repo):
    user_mock_repo.find_by_id.return_value = MagicMock(id=2, name='User 1')
    user_mock_repo.calculate_total_income.return_value = 300
    category = MagicMock(id=3, name='Category 1', percentage=20)
    category_mock_repo.find_by_id.return_value = category
    planned_spending = service._calculate_planned_spending_for_user_by_category(
        user_id=2,
        category_id=3
    )

    assert planned_spending is not None
    assert planned_spending == 300 * category.percentage / 100
    assert user_mock_repo.calculate_total_income.call_count == 1
    assert category_mock_repo.find_by_id.call_count == 1


def test_generate_budget_entries_for_user_by_category(service, user_mock_repo, category_mock_repo):
    percentage = 20
    expenses = [
        ExpenseCategoryEntity(id=1, name='Rent', type_='expense', percentage=percentage)
    ]

    user_mock_repo.get_expense_categories_idx.return_value = [expenses[0].id]
    user = MagicMock(id=1, name='User 1', email='u1@gmail.com')
    total_expense = 3000
    user_mock_repo.calculate_total_expenses.return_value = total_expense
    user_mock_repo.find_by_id.return_value = user
    total_income = 8000
    user_mock_repo.calculate_total_income.return_value = total_income
    category_mock_repo.find_by_id.return_value = expenses[0]

    expected_budget = service.generate_budget_entries_for_user(user_id=1)
    budget_for_one_user = CreateCategorizedBudgetEntryDto(
        category=expenses[0].name,
        planned_amount=total_income * percentage / 100,
        actual_amount=total_expense,
    )
    assert expected_budget is not None
    assert expected_budget == [
        budget_for_one_user.to_dict()
    ]

    assert user_mock_repo.find_by_id.call_count == 1
    assert user_mock_repo.calculate_total_expenses.call_count == 1
    assert user_mock_repo.calculate_total_income.call_count == 1
    assert category_mock_repo.find_by_id.call_count == 3
