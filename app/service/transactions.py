from dataclasses import dataclass
from typing import Any
from werkzeug.exceptions import NotFound
from app.persistent.repository import (
    IncomeRepository,
    UserRepository,
    ExpenseRepository,
    TransactionRepository, CategoryRepository
)
from app.persistent.entity import (
    IncomeEntity,
    ExpenseEntity,
    TransactionEntity
)
from app.service.dto import CreateTransactionDto, TransactionDto, CategoryDto

import logging

logging.basicConfig(level=logging.INFO)


@dataclass
class TransactionService:
    income_repository: IncomeRepository
    expense_repository: ExpenseRepository
    transaction_repository: TransactionRepository
    user_repository: UserRepository
    category_repository: CategoryRepository

    def get_by_id(self, transaction_id: int) -> dict[str, Any]:
        transaction = self.transaction_repository.find_by_id(transaction_id)
        if not transaction:
            raise NotFound('Transaction not found')

        return TransactionDto.from_transaction_entity(transaction).to_dict()

    def create_transaction(self, transaction_dto: CreateTransactionDto) -> TransactionEntity:

        category = self.category_repository.find_by_id(transaction_dto.category_id)
        if not category:
            raise NotFound('Category not found')

        category_type = category.type_
        if category_type == 'income':
            transaction = IncomeEntity(
                amount=transaction_dto.amount,
                user_id=transaction_dto.user_id,
                category_id=transaction_dto.category_id,
            )
        else:
            transaction = ExpenseEntity(
                amount=transaction_dto.amount,
                user_id=transaction_dto.user_id,
                category_id=transaction_dto.category_id
            )
        return transaction

    def add_transaction(self, transaction_dto: CreateTransactionDto) -> dict[str, Any]:
        user = self.user_repository.find_by_id(transaction_dto.user_id)
        if not user:
            raise NotFound('User not found')

        transaction = self.create_transaction(transaction_dto)

        if isinstance(transaction, IncomeEntity):
            self.income_repository.save_or_update(transaction)
        elif isinstance(transaction, ExpenseEntity):
            self.expense_repository.save_or_update(transaction)

        return TransactionDto.from_transaction_entity(transaction).to_dict()

    def update_transaction_amount(self, transaction_id: int, new_amount: int) -> dict[str, Any]:
        transaction = self.transaction_repository.find_by_id(transaction_id)
        if not transaction:
            raise NotFound('Transaction not found')

        transaction.change_amount(new_amount)

        self.transaction_repository.save_or_update(transaction)
        return TransactionDto.from_transaction_entity(transaction).to_dict()

    def get_all_transactions_for_category(self, category_name: str) -> list[dict[str, Any]]:
        category = self.category_repository.find_by_name(category_name)

        if not category:
            raise NotFound('Category not found')

        transactions = category.income_transactions if category.type_ == 'income' else category.expense_transactions
        return [TransactionDto.from_transaction_entity(t).to_dict() for t in transactions]

    def get_transactions_higher_than(self, expected_amount: float, transaction_type: str) -> list[dict[str, Any]]:

        if transaction_type == 'INCOME':
            return [TransactionDto.from_transaction_entity(t).to_dict() for t in
                    self.income_repository.find_higher_than(expected_amount)]
        if transaction_type == 'EXPENSE':
            return [TransactionDto.from_transaction_entity(t).to_dict() for t in
                    self.expense_repository.find_higher_than(expected_amount)]
