import logging
from typing import Any, Self
from sqlalchemy import (
    Integer,
    BigInteger,
    String,
    Boolean,
    ForeignKey,
    DateTime,
    Date
)
import datetime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.persistent.configuration import sa
from werkzeug.security import check_password_hash
from enum import Enum


class Frequency(Enum):
    DAILY = 0
    WEEKLY = 1
    MONTHLY = 2


class UserEntity(sa.Model):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    password: Mapped[str] = mapped_column(String(512), nullable=False)
    email: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[str] = mapped_column(String(15), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=False)

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
            'role': self.role,
        }

    def check_password(self, password: str) -> bool:
        return check_password_hash(self.password, password)

    def __str__(self) -> str:
        return f'USER: {self.id} {self.name}'

    def __repr__(self) -> str:
        return str(self)


class ActivationTokenEntity(sa.Model):
    __tablename__ = 'activation_tokens'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    token: Mapped[str] = mapped_column(String(255), nullable=False)
    # timestamp ktory bedzie mowil kiedy sie konczy token
    timestamp: Mapped[int] = mapped_column(BigInteger)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'))

    user: Mapped[UserEntity] = relationship('UserEntity', uselist=False)

    def is_active(self) -> bool:
        return self.timestamp > datetime.datetime.now(datetime.UTC).timestamp()


class TransactionEntity(sa.Model):
    __tablename__ = 'transactions'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    amount: Mapped[int] = mapped_column(Integer, nullable=False)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'))
    type_: Mapped[str] = mapped_column(String(50))

    __mapper_args__ = {
        "polymorphic_on": type_,
        'polymorphic_identity': 'transaction'
    }

    def to_dict(self) -> dict[str, Any]:
        return {
            'id': self.id,
            'amount': self.amount,
            'user_id': self.user_id,
            'type': self.type_,
        }

    def change_amount(self, amount: int) -> None:
        if self.amount == amount:
            return
        self.amount = amount


class IncomeEntity(TransactionEntity):
    __tablename__ = 'incomes'

    id: Mapped[int] = mapped_column(Integer, ForeignKey('transactions.id'), primary_key=True)
    category_id: Mapped[int] = mapped_column(Integer, ForeignKey('income_categories.id'), nullable=False)

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

    income_transactions: Mapped[list[IncomeEntity]] = relationship(
        'IncomeEntity',
        backref='category',
        cascade='all, delete-orphan'
    )

    __mapper_args__ = {
        'polymorphic_identity': 'income'
    }


class ExpenseCategoryEntity(CategoryEntity):
    __tablename__ = 'expense_categories'

    id: Mapped[int] = mapped_column(Integer, ForeignKey('categories.id'), primary_key=True)
    percentage: Mapped[int] = mapped_column(Integer, default=10)

    expense_transactions: Mapped[list[ExpenseEntity]] = relationship(
        'ExpenseEntity',
        backref='category',
        cascade='all, delete-orphan'
    )

    __mapper_args__ = {
        'polymorphic_identity': 'expense'
    }

    def to_dict(self) -> dict[str, Any]:
        data = super().to_dict()
        data['percentage'] = float(self.percentage)
        return data

    def __str__(self):
        return f'id {id}  percentage {self.percentage}'

    def __repr__(self):
        return str(self)


class RecurringTransactionEntity(sa.Model):
    __tablename__ = 'recurring_transactions'

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    amount: Mapped[int] = mapped_column(Integer, nullable=False)
    frequency: Mapped[Frequency] = mapped_column(default=Frequency.MONTHLY)
    user_id: Mapped[int] = mapped_column(Integer, ForeignKey('users.id'), nullable=False)
    next_due_date: Mapped[datetime.date] = mapped_column(Date, nullable=False)

    type_: Mapped[str] = mapped_column(String(50))

    __mapper_args__ = {
        "polymorphic_on": type_,
        "polymorphic_identity": 'recurring_transaction'
    }

    def is_invalid(self, current_date: datetime.date) -> bool:
        return self.next_due_date < current_date

    def is_next_due_date_after_current(self, current_date: datetime.date) -> bool:
        return self.next_due_date > current_date

    def are_dates_equal(self, current_date: datetime.date) -> bool:
        return self.next_due_date == current_date

    def is_valid_date(self, current_date: datetime.date) -> bool:
        return self.next_due_date >= current_date

    def to_dict(self) -> dict[str, Any]:
        return {
            "id": self.id,
            "amount": float(self.amount),
            "frequency": self.frequency.name,
            "user_id": self.user_id,
            "next_due_date": self.next_due_date.strftime("%Y-%m-%d")
        }


class IncomeRecurringTransactionEntity(RecurringTransactionEntity):
    __tablename__ = 'income_recurring_transactions'

    id: Mapped[int] = mapped_column(Integer, ForeignKey('recurring_transactions.id'), primary_key=True)
    category_id: Mapped[IncomeCategoryEntity] = mapped_column(Integer, ForeignKey('income_categories.id'))

    category: Mapped['IncomeCategoryEntity'] = relationship(
        'IncomeCategoryEntity',
        backref='income_recurring_transactions')

    __mapper_args__ = {
        "polymorphic_identity": 'income'
    }

    def to_dict(self) -> dict[str, Any]:
        data = super().to_dict()
        data['category_id'] = self.category_id
        return data


class ExpenseRecurringTransactionEntity(RecurringTransactionEntity):
    __tablename__ = 'expense_recurring_transactions'
    id: Mapped[int] = mapped_column(Integer, ForeignKey('recurring_transactions.id'), primary_key=True)

    category_id: Mapped[ExpenseCategoryEntity] = mapped_column(Integer, ForeignKey('expense_categories.id'))

    category: Mapped[ExpenseCategoryEntity] = relationship(
        'ExpenseCategoryEntity',
        backref='expense_recurring_transactions'
    )
    __mapper_args__ = {
        "polymorphic_identity": 'expense'
    }

    def to_dict(self) -> dict[str, Any]:
        data = super().to_dict()
        data['category_id'] = self.category_id
        return data
