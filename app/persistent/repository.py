from typing import Any
import logging
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import select

from app.persistent.configuration import sa
from app.persistent.entity import (
    UserEntity,
    TransactionEntity,
    IncomeEntity,
    ExpenseEntity,
    CategoryEntity,
    IncomeCategoryEntity,
    ExpenseCategoryEntity,
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
        return self.sa.session.execute(stmt).all()

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

    def calculate_total_income(self, user_id: int) -> float:
        user = self.find_by_id(user_id)
        transactions = user.transactions
        return sum([t for t in transactions if t.type_ == 'income'])


class TransactionRepository(CrudRepositoryORM[TransactionEntity]):
    def __init__(self, db: SQLAlchemy) -> None:
        super().__init__(db, TransactionEntity)

    def find_higher_than(self, amount: float) -> list[TransactionEntity]:
        stmt = select(TransactionEntity).where(TransactionEntity.amount > amount)
        return self.sa.session.execute(stmt).all()


class IncomeRepository(CrudRepositoryORM[IncomeEntity]):
    def __init__(self, db: SQLAlchemy) -> None:
        super().__init__(db, IncomeEntity)


class ExpenseRepository(CrudRepositoryORM[ExpenseEntity]):
    def __init__(self, db: SQLAlchemy) -> None:
        super().__init__(db, ExpenseEntity)


class CategoryRepository(CrudRepositoryORM[CategoryEntity]):
    def __init__(self, db: SQLAlchemy) -> None:
        super().__init__(db, CategoryEntity)


class IncomeCategoryRepository(CrudRepositoryORM[IncomeCategoryEntity]):
    def __init__(self, db: SQLAlchemy) -> None:
        super().__init__(db, IncomeCategoryEntity)


class ExpenseCategoryRepository(CrudRepositoryORM[ExpenseCategoryEntity]):
    def __init__(self, db: SQLAlchemy) -> None:
        super().__init__(db, ExpenseCategoryEntity)


user_repository = UserRepository(sa)
transaction_repository = TransactionRepository(sa)
income_repository = IncomeRepository(sa)
expense_repository = ExpenseRepository(sa)
category_repository = CategoryRepository(sa)
income_category_repository = IncomeCategoryRepository(sa)
expense_category_repository = ExpenseCategoryRepository(sa)
