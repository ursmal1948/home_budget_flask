from typing import Any, Self
from decimal import Decimal
from sqlalchemy import (
    Integer,
    String,
    DECIMAL,
    ForeignKey
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.persistent.configuration import sa


class UserEntity(sa.Model):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    password: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False)

    transactions: Mapped[list['TransactionEntity']] = relationship(
        'TransactionEntity',
        backref='user'
    )

    def to_dict(self) -> dict[str, Any]:
        return {
            'id': self.id,
            'name': self.name,
            'password': self.password,
            'email': self.email,
        }


class TransactionEntity(sa.Model):
    __tablename__ = 'transactions'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    amount: Mapped[Decimal] = mapped_column(DECIMAL(10, 2), nullable=False)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'))
    type_: Mapped[str] = mapped_column(String(50))

    __mapper_args__ = {
        "polymorphic_on": type_,
        'polymorphic_identity': 'transaction'
    }

    def to_dict(self) -> dict[str, Any]:
        return {
            'id': self.id,
            'amount': float(self.amount),
            'user_id': self.user_id,
            'type': self.type_,
        }


class IncomeEntity(TransactionEntity):
    __tablename__ = 'incomes'

    id: Mapped[int] = mapped_column(Integer, ForeignKey('transactions.id'), primary_key=True)
    category_id: Mapped[int] = mapped_column(Integer, ForeignKey('income_categories.id'), nullable=False)

    category: Mapped['IncomeCategoryEntity'] = relationship(
        'IncomeCategoryEntity',
        backref='income_transactions'
    )

    __mapper_args__ = {
        'polymorphic_identity': 'income'
    }

    def to_dict(self) -> dict[str, Any]:
        data = super().to_dict()
        data['category_id'] = self.category_id
        return data


class ExpenseEntity(TransactionEntity):
    __tablename__ = 'expenses'

    id: Mapped[int] = mapped_column(Integer, ForeignKey('transactions.id'), primary_key=True)
    category_id: Mapped[int] = mapped_column(Integer, ForeignKey('expense_categories.id'), nullable=False)

    category: Mapped['ExpenseCategoryEntity'] = relationship(
        'ExpenseCategoryEntity',
        backref='expense_transactions'
    )
    __mapper_args__ = {
        'polymorphic_identity': 'expense'
    }


class CategoryEntity(sa.Model):
    __tablename__ = 'categories'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    type_: Mapped[str] = mapped_column(String(50))
    __mapper_args__ = {
        'polymorphic_on': type_,
        'polymorphic_identity': 'category'
    }

    def to_dict(self) -> dict[str, Any]:
        return {
            'id': self.id,
            'name': self.name,
            'type': self.type_,
        }


class IncomeCategoryEntity(CategoryEntity):
    __tablename__ = 'income_categories'

    id: Mapped[int] = mapped_column(Integer, ForeignKey('categories.id'), primary_key=True)

    __mapper_args__ = {
        'polymorphic_identity': 'income'
    }


class ExpenseCategoryEntity(CategoryEntity):
    __tablename__ = 'expense_categories'

    id: Mapped[int] = mapped_column(Integer, ForeignKey('categories.id'), primary_key=True)
    percentage: Mapped[Decimal] = mapped_column(DECIMAL(10, 2), default=10)

    __mapper_args__ = {
        'polymorphic_identity': 'expense'
    }

    def to_dict(self) -> dict[str, Any]:
        data = super().to_dict()
        data['percentage'] = float(self.percentage)
        return data
