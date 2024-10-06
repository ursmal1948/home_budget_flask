from dataclasses import dataclass
from werkzeug.exceptions import NotFound
from app.persistent.repository import (
    TransactionRepository,
    UserRepository,
    CategoryRepository,
)
from app.service.dto import CreateCategorizedBudgetEntryDto


@dataclass
class BudgetPlanningService:
    user_repository: UserRepository
    category_repository: CategoryRepository
    transaction_repository: TransactionRepository

    def calculate_actual_spending_for_category(self, user_id: int, category_id: int) -> int:
        category = self.category_repository.find_by_id(category_id)
        if not category or category.type_ == 'income':
            raise ValueError('Incorrect category')

        return self.user_repository.calculate_total_expenses(user_id, category.id)

    def calculate_planned_spending_for_user_by_category(self, user_id: int, category_id: int) -> float:
        user = self.user_repository.find_by_id(user_id)
        category = self.category_repository.find_by_id(category_id)

        if not user:
            raise NotFound('User not found')
        user_income = self.user_repository.calculate_total_income(user_id)
        return user_income * category.percentage / 100

    def _build_single_budget_entry(self, user_id: int, category_id: int):
        planned = self.calculate_planned_spending_for_user_by_category(user_id, category_id)
        actual = self.calculate_actual_spending_for_category(user_id, category_id)
        category = self.category_repository.find_by_id(category_id)
        return CreateCategorizedBudgetEntryDto(category.name, planned, actual).to_dict()

    def generate_budget_entries(self, user_id: int):

        expense_categories_idx = self.user_repository.get_expense_categories_idx(user_id)
        return [self._build_single_budget_entry(user_id, e) for e in expense_categories_idx]


"""
    [
    {
        "category": "Rent", dla tej kategorii expense percenrage to 40%
        "planned_amount": 2600.0,
        "actual_amount": 1500.0,
        "difference": 1100.0
    },
    {
        "category": "Groceries", dla tej kategorii  expense percenrage to 30%
        "planned_amount": 1950.0,
        "actual_amount": 500.0,
        "difference": 1450.0
    },
    {
        "category": "Entertainment", dla tej kategorii  expense percenrage to 30%
        "planned_amount": 1950.0,
        "actual_amount": 200.0,
        "difference": 1750.0
    }
]

    """
