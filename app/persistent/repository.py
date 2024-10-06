from typing import Any
import logging
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import select
from sqlalchemy.orm import joinedload

from app.persistent.configuration import sa
from app.persistent.entity import (
    UserEntity,
    ActivationTokenEntity,
    TransactionEntity,
    IncomeEntity,
    ExpenseEntity,
    CategoryEntity,
    IncomeCategoryEntity,
    ExpenseCategoryEntity,
    RecurringTransactionEntity,
    IncomeRecurringTransactionEntity,
    ExpenseRecurringTransactionEntity,
)

logging.basicConfig(level=logging.INFO)


class CrudRepositoryORM[T:sa.Model]:
    def __init__(self, db: SQLAlchemy, entity_type: Any) -> None:
        self.sa = db
        self.entity_type = entity_type

    def save_or_update(self, entity: T) -> None:
        self.sa.session.add(self.sa.session.merge(entity) if entity.id else entity)
        self.sa.session.commit()

    def save_or_update_many(self, entities: list[T]) -> None:
        self.sa.session.add_all(entities)
        self.sa.session.commit()

    def find_by_id(self, entity_id: int) -> T | None:
        stmt = select(self.entity_type).filter_by(id=entity_id)
        return self.sa.session.execute(stmt).scalar_one_or_none()

    def find_all(self) -> list[T]:
        stmt = select(self.entity_type)
        return self.sa.session.execute(stmt).scalars().all()

    def delete_by_id(self, entity_id: int) -> None:
        entity = self.find_by_id(entity_id)
        self.sa.session.delete(entity)
        self.sa.session.commit()

    def delete_all(self) -> None:
        entities = self.find_all()
        for e in entities:
            self.sa.session.delete(e)
            self.sa.session.commit()


class UserRepository(CrudRepositoryORM[UserEntity]):
    def __init__(self, db: SQLAlchemy) -> None:
        super().__init__(db, UserEntity)

    def find_by_email(self, email: str) -> UserEntity | None:
        stmt = select(UserEntity).filter_by(email=email)
        return self.sa.session.execute(stmt).scalar_one_or_none()

    def find_by_name(self, name: str) -> UserEntity | None:
        stmt = select(UserEntity).filter_by(name=name)
        return self.sa.session.execute(stmt).scalar_one_or_none()

    def calculate_total_income(self, user_id: int) -> int:
        user = self.find_by_id(user_id)
        transactions = user.transactions
        return sum([t.amount for t in transactions if t.type_ == 'income'])

    def calculate_total_expenses(self, user_id: int, category_id: int) -> int:
        user = self.find_by_id(user_id)
        return sum([t.amount for t in user.transactions if t.type_ == 'expense' and t.category_id == category_id])

    def get_expense_categories_idx(self, user_id: int) -> list[int]:
        transactions = self.find_by_id(user_id).transactions
        expenses = [t for t in transactions if t.type_ == 'expense']
        return list(set([e.category_id for e in expenses]))


class ActivationTokenRepository(CrudRepositoryORM[ActivationTokenEntity]):
    def __init__(self, db: SQLAlchemy) -> None:
        super().__init__(db, ActivationTokenEntity)

    def find_by_token(self, token: str) -> ActivationTokenEntity | None:
        stmt = select(self.entity_type).filter_by(token=token).options(
            joinedload(ActivationTokenEntity.user)
        )
        return self.sa.session.execute(stmt).scalar_one_or_none()


class TransactionRepository(CrudRepositoryORM[TransactionEntity]):
    def __init__(self, db: SQLAlchemy) -> None:
        super().__init__(db, TransactionEntity)


class IncomeRepository(CrudRepositoryORM[IncomeEntity]):
    def __init__(self, db: SQLAlchemy) -> None:
        super().__init__(db, IncomeEntity)

    def find_higher_than(self, amount: float) -> list[IncomeEntity]:
        stmt = select(IncomeEntity).where(IncomeEntity.amount > amount)
        return self.sa.session.execute(stmt).scalars().all()


class ExpenseRepository(CrudRepositoryORM[ExpenseEntity]):
    def __init__(self, db: SQLAlchemy) -> None:
        super().__init__(db, ExpenseEntity)

    def find_higher_than(self, amount: float) -> list[ExpenseEntity]:
        stmt = select(ExpenseEntity).where(ExpenseEntity.amount > amount)
        return self.sa.session.execute(stmt).scalars().all()


class CategoryRepository(CrudRepositoryORM[CategoryEntity]):
    def __init__(self, db: SQLAlchemy) -> None:
        super().__init__(db, CategoryEntity)

    def find_by_name(self, name: str) -> CategoryEntity | None:
        stmt = select(self.entity_type).filter_by(name=name)
        return self.sa.session.execute(stmt).scalar_one_or_none()

    def delete_by_name(self, name: str) -> None:
        entity = self.find_by_name(name)
        self.sa.session.delete(entity)
        self.sa.session.commit()


class IncomeCategoryRepository(CrudRepositoryORM[IncomeCategoryEntity]):
    def __init__(self, db: SQLAlchemy) -> None:
        super().__init__(db, IncomeCategoryEntity)


class ExpenseCategoryRepository(CrudRepositoryORM[ExpenseCategoryEntity]):
    def __init__(self, db: SQLAlchemy) -> None:
        super().__init__(db, ExpenseCategoryEntity)

    def calculate_all_percentages(self) -> float:
        expense_categories = self.find_all()

        return sum([c.percentage for c in expense_categories])


class RecurringTransactionRepository(CrudRepositoryORM[RecurringTransactionEntity]):
    def __init__(self, db: SQLAlchemy):
        super().__init__(db, RecurringTransactionEntity)


class ExpenseRecurringTransactionRepository(CrudRepositoryORM[ExpenseRecurringTransactionEntity]):
    def __init__(self, db: SQLAlchemy):
        super().__init__(db, ExpenseRecurringTransactionEntity)


class IncomeRecurringTransactionRepository(CrudRepositoryORM[IncomeRecurringTransactionEntity]):
    def __init__(self, db: SQLAlchemy):
        super().__init__(db, IncomeRecurringTransactionEntity)


user_repository = UserRepository(sa)
transaction_repository = TransactionRepository(sa)
income_repository = IncomeRepository(sa)
expense_repository = ExpenseRepository(sa)
category_repository = CategoryRepository(sa)
income_category_repository = IncomeCategoryRepository(sa)
expense_category_repository = ExpenseCategoryRepository(sa)
activation_token_repository = ActivationTokenRepository(sa)
recurring_transaction_repository = RecurringTransactionRepository(sa)
income_recurring_transaction_repository = IncomeRecurringTransactionRepository(sa)
expense_recurring_transaction_repository = ExpenseRecurringTransactionRepository(sa)
