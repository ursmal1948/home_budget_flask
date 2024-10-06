from app.service.users import UserService, UserSecurityService
from app.service.categories import CategoryService
from app.service.transactions import TransactionService
from app.service.budget_planning import BudgetPlanningService
from app.service.recurring_transactions import RecurringTransactionsService
from app.persistent.repository import (
    user_repository,
    activation_token_repository,
    category_repository,
    income_category_repository,
    income_repository,
    expense_repository,
    expense_category_repository,
    transaction_repository,
    income_recurring_transaction_repository,
    expense_recurring_transaction_repository,
    recurring_transaction_repository,
)

user_service = UserService(user_repository)
user_security_service = UserSecurityService(user_repository, activation_token_repository)
category_service = CategoryService(category_repository, income_category_repository, expense_category_repository)
transaction_service = TransactionService(
    income_repository,
    expense_repository,
    transaction_repository,
    user_repository,
    category_repository
)
budget_planning_service = BudgetPlanningService(
    user_repository,
    category_repository,
    transaction_repository
)

recurring_transaction_service = RecurringTransactionsService(
    income_recurring_transaction_repository,
    expense_recurring_transaction_repository,
    user_repository,
    category_repository,
    income_repository,
    expense_repository,
    recurring_transaction_repository
)
