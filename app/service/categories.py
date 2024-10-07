from dataclasses import dataclass
from typing import Any
from werkzeug.exceptions import NotFound
from app.persistent.repository import (
    CategoryRepository,
    IncomeCategoryRepository,
    ExpenseCategoryRepository
)

from app.persistent.entity import (
    IncomeCategoryEntity,
    ExpenseCategoryEntity
)
from app.service.dto import CategoryDto, CreateCategoryDto

import logging

logging.basicConfig(level=logging.INFO)


@dataclass
class CategoryService:
    category_repository: CategoryRepository
    income_category_repository: IncomeCategoryRepository
    expense_category_repository: ExpenseCategoryRepository

    def calculate_percentages_sum(self, new_percentage: float) -> float:
        expense_percentages = self.expense_category_repository.calculate_all_percentages()
        return new_percentage + expense_percentages

    def add_category(self, create_category_dto: CreateCategoryDto) -> \
            dict[str, Any]:
        name = create_category_dto.name

        if self.category_repository.find_by_name(name):
            raise ValueError('Category already exists')

        category_type = create_category_dto.category_type
        if category_type == 'income':
            entity = IncomeCategoryEntity(name=name)
            self.income_category_repository.save_or_update(entity)
        else:
            percentage = create_category_dto.percentage
            if self.calculate_percentages_sum(percentage) > 100:
                raise ValueError('The sum of percentages cannot exceed 100')

            entity = ExpenseCategoryEntity(name=name, percentage=percentage)
            self.expense_category_repository.save_or_update(entity)

        return CategoryDto.from_category_entity(entity).to_dict()

    def get_by_id(self, category_id: int) -> dict[str, Any]:
        category = self.category_repository.find_by_id(category_id)
        if not category:
            raise NotFound('Category not found')

        return CategoryDto.from_category_entity(category).to_dict()

    def get_by_name(self, name: str) -> dict[str, Any]:
        category = self.category_repository.find_by_name(name)
        if not category:
            raise NotFound('Category not found')

        return CategoryDto.from_category_entity(category).to_dict()

    def delete_by_name(self, name: str) -> None:
        if not self.category_repository.find_by_name(name):
            raise NotFound('Category not found')

        self.category_repository.delete_by_name(name)

    def update_expense_percentage(self, category_id: int, new_percentage: int) -> dict[str, Any]:
        category = self.expense_category_repository.find_by_id(category_id)

        if not category:
            raise NotFound('Category not found')

        if self.calculate_percentages_sum(new_percentage) - category.percentage > 100:
            raise ValueError('The sum of percentages cannot exceessd 100')

        category.change_precentage(percentage=new_percentage)
        self.category_repository.save_or_update(category)
        return CategoryDto.from_category_entity(category).to_dict()
