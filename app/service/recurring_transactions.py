from dataclasses import dataclass
from typing import Any
from flask import current_app
import datetime

from datetime import timedelta
from app.persistent.repository import (
    RecurringTransactionRepository,
    UserRepository,
    CategoryRepository,
    IncomeRepository,
    IncomeRecurringTransactionRepository,
    ExpenseRecurringTransactionRepository, ExpenseRepository
)
from flask import Flask
from app.persistent.entity import IncomeEntity, Frequency, ExpenseEntity
from app.persistent.entity import (
    RecurringTransactionEntity,
    IncomeCategoryEntity,
    ExpenseCategoryEntity,
    IncomeRecurringTransactionEntity,
    ExpenseRecurringTransactionEntity,
)
from app.service.dto import CreateRecurringTransactionDto
import logging

logging.basicConfig(level=logging.INFO)
# from app.main import scheduler
from flask_apscheduler import APScheduler


@dataclass
class RecurringTransactionsService:
    income_recurring_transaction_repository: IncomeRecurringTransactionRepository
    expense_recurring_transaction_repository: ExpenseRecurringTransactionRepository
    user_repository: UserRepository
    category_repository: CategoryRepository
    income_repository: IncomeRepository
    expense_repository: ExpenseRepository
    recurring_transaction_repository: RecurringTransactionRepository

    def create_recurring_transaction(
            self,
            dto: CreateRecurringTransactionDto) -> RecurringTransactionEntity:

        user_id = dto.user_id

        current_date = (datetime.datetime.now()).date()

        if not dto.is_valid_date(current_date):
            raise ValueError('Invalid date')

        if not self.user_repository.find_by_id(user_id):
            raise ValueError('User not found')

        category = self.category_repository.find_by_id(dto.category_id)
        if not category:
            raise ValueError('Category not found')

        if isinstance(category, IncomeCategoryEntity):
            recurring_transaction = IncomeRecurringTransactionEntity(
                amount=dto.amount,
                frequency=dto.frequency,
                user_id=dto.user_id,
                category_id=category.id,
                next_due_date=dto.next_due_date
            )
            self.income_recurring_transaction_repository.save_or_update(recurring_transaction)
        else:
            recurring_transaction = ExpenseRecurringTransactionEntity(
                amount=dto.amount,
                frequency=dto.frequency,
                user_id=dto.user_id,
                category_id=category.id,
                next_due_date=dto.next_due_date
            )

            self.expense_recurring_transaction_repository.save_or_update(recurring_transaction)
        return recurring_transaction

    def _process_recurring_transaction(self, transaction: RecurringTransactionEntity):

        if isinstance(transaction, IncomeRecurringTransactionEntity):
            self.create_income_transaction(transaction)
        elif isinstance(transaction, ExpenseRecurringTransactionEntity):
            self.create_expense_transaction(transaction)

        return transaction.to_dict()

    def _validate_date_of_transaction(self, transaction: RecurringTransactionEntity, current_date: datetime.date):
        if transaction.is_invalid(current_date):
            self.recurring_transaction_repository.delete_by_id(transaction.id)
            return None

        if transaction.is_next_due_date_after_current(current_date):
            return None

        if transaction.are_dates_equal(current_date):
            return transaction

    def process_recurring_transactions(self):

        current_date = (datetime.datetime.now()).date()
        entities = self.recurring_transaction_repository.find_all()

        transactions_to_process = [t for t in entities if
                                   self._validate_date_of_transaction(t, current_date) is not None]
        if not transactions_to_process:
            return []

        return [self._process_recurring_transaction(e) for e in transactions_to_process]

    def _update_next_due_date(self, transaction: RecurringTransactionEntity):
        frequency = transaction.frequency
        if frequency == Frequency.DAILY:
            transaction.next_due_date += timedelta(days=1)

        elif frequency == Frequency.WEEKLY:
            transaction.next_due_date += timedelta(weeks=1)
        else:

            transaction.next_due_date += timedelta(weeks=4)

    def create_income_transaction(self, transaction: IncomeRecurringTransactionEntity):
        income_entity = IncomeEntity(
            amount=transaction.amount,
            user_id=transaction.user_id,
            category_id=transaction.category_id,
        )
        self._update_next_due_date(transaction)
        self.income_repository.save_or_update(income_entity)
        self.income_recurring_transaction_repository.save_or_update(transaction)

    def create_expense_transaction(self, transaction: ExpenseRecurringTransactionEntity):
        expense_entity = ExpenseEntity(
            amount=transaction.amount,
            user_id=transaction.user_id,
            category_id=transaction.category_id,
        )
        self._update_next_due_date(transaction)
        self.expense_repository.save_or_update(expense_entity)
        self.expense_recurring_transaction_repository.save_or_update(transaction)
