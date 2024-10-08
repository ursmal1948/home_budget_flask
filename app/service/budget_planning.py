from dataclasses import dataclass
from werkzeug.exceptions import NotFound
from typing import Any
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

    def _calculate_actual_spending_for_category(self, user_id: int, category_id: int) -> int:
        category = self.category_repository.find_by_id(category_id)
        return self.user_repository.calculate_total_expenses(user_id, category.id)

    def _calculate_planned_spending_for_user_by_category(self, user_id: int, category_id: int) -> float:
        category = self.category_repository.find_by_id(category_id)
        user_income = self.user_repository.calculate_total_income(user_id)
        return user_income * category.percentage / 100

    def _build_single_budget_entry(self, user_id: int, category_id: int) -> dict[str, Any]:
        planned = self._calculate_planned_spending_for_user_by_category(user_id, category_id)
        actual = self._calculate_actual_spending_for_category(user_id, category_id)
        category = self.category_repository.find_by_id(category_id)
        return CreateCategorizedBudgetEntryDto(category.name, planned, actual).to_dict()

    def generate_budget_entries_for_user(self, user_id: int):
        user = self.user_repository.find_by_id(user_id)
        if not user:
            raise NotFound('User not found')

        expense_categories_idx = self.user_repository.get_expense_categories_idx(user_id)
        return [self._build_single_budget_entry(user_id, e) for e in expense_categories_idx]

    def generate_budget_entries_for_all_users(self):
        all_users = [u for u in self.user_repository.find_all()]
        if not all_users:
            raise NotFound('No users found')
        return [(f'{u.id}.{u.name}', self.generate_budget_entries_for_user(u.id)) for u in all_users]
