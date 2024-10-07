import logging
from dataclasses import dataclass
from typing import Self, Any
from app.persistent.entity import UserEntity, TransactionEntity, CategoryEntity, ExpenseCategoryEntity, \
    RecurringTransactionEntity
from app.persistent.entity import Frequency
import datetime

# tutaj rejestrue uzytkownika ktory chce byc admine. Ale nigdy nie bedziemy podawac
# roli jawnie. ale dla nas bedzie latwo tworzyc uzytkownikow z roznymi rolami.
# nie tworzyc usera ktoremu podaje role.

# wszelkie konwersje z dto i do dto umieszacamy w klasach ponizej.
# cala robote konwersujaca przechwytujaca zajmuja sie te modele.
# skoro masz dto doloz walidacje na koniec.
# walidacja dla danych ktore masz w dto.
import logging

logging.basicConfig(level=logging.INFO)


@dataclass
class RegisterUserDto:
    name: str
    email: str
    password: str
    password_confirmation: str
    role: str

    def check_passwords(self) -> bool:
        return self.password == self.password_confirmation

    def with_password(self, new_password: str) -> Self:
        return RegisterUserDto(
            name=self.name,
            email=self.email,
            password=new_password,
            password_confirmation=self.password_confirmation,
            role=self.role,
        )

    def to_user_entity(self) -> UserEntity:
        return UserEntity(
            name=self.name,
            email=self.email,
            password=self.password,
            role=self.role,
            is_active=False,
        )

    @classmethod
    def from_dict(cls, data: dict[str, str]) -> Self:
        return cls(
            name=data['name'],
            email=data['email'],
            password=data['password'],
            password_confirmation=data['password_confirmation'],
            role=data['role'],
        )


@dataclass
class UserDto:
    id: int
    name: str
    email: str
    role: str

    def to_dict(self) -> dict[str, Any]:
        return {
            'id': self.id,
            'name': self.name,
            'email': self.email,
            'role': self.role,
        }

    @classmethod
    def from_user_entity(cls, user_entity: UserEntity) -> Self:
        return cls(
            user_entity.id,
            user_entity.name,
            user_entity.email,
            user_entity.role,
        )


@dataclass
class CreateUserDto:
    name: str
    email: str
    password: str
    role: str

    @classmethod
    def from_dict(cls, data: dict[str, str]) -> Self:
        return cls(
            name=data['name'],
            email=data['email'],
            password=data['password'],
            role=data['role'],
        )


@dataclass
class CreateTransactionDto:
    amount: int
    user_id: int
    category_id: int

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Self:
        return cls(
            amount=int(data['amount']),
            user_id=data['user_id'],
            category_id=data['category_id'],
        )


@dataclass
class TransactionDto:
    id: int
    amount: int
    user_id: int
    category_id: int
    type_: str

    def to_dict(self) -> dict[str, Any]:
        return {
            'id': self.id,
            'amount': self.amount,
            'user_id': self.user_id,
            'category_id': self.category_id,
            'type': self.type_,
        }

    @classmethod
    def from_transaction_entity(cls, transaction_entity: TransactionEntity) -> Self:
        return cls(
            id=transaction_entity.id,
            amount=int(transaction_entity.amount),
            user_id=transaction_entity.user_id,
            category_id=transaction_entity.category_id,
            type_=transaction_entity.type_
        )


@dataclass
class RecurringTransactionDto:
    id: int
    amount: int
    user_id: int
    category_id: int
    type_: str
    frequency: Frequency
    next_due_date: datetime.date

    def to_dict(self) -> dict[str, Any]:
        return {
            'id': self.id,
            'amount': self.amount,
            'user_id': self.user_id,
            'category_id': self.category_id,
            'type': self.type_,
            'frequency': self.frequency,
            'next_due_date': self.next_due_date,
        }

    @classmethod
    def from_transaction_entity(cls, transaction_entity: RecurringTransactionEntity) -> Self:
        return cls(
            id=transaction_entity.id,
            amount=int(transaction_entity.amount),
            user_id=transaction_entity.user_id,
            category_id=transaction_entity.category_id,
            frequency=transaction_entity.frequency,
            next_due_date=transaction_entity.next_due_date,
            type_=transaction_entity.type_
        )


@dataclass
class CreateRecurringTransactionDto:
    amount: int
    frequency: Frequency
    next_due_date: datetime
    category_id: int
    user_id: int

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Self:
        logging.info(data['next_due_date'])
        return cls(
            amount=int(data['amount']),
            frequency=Frequency[data['frequency']],
            next_due_date=datetime.datetime.strptime(data['next_due_date'], '%Y-%m-%d').date(),
            category_id=data['category_id'],
            user_id=data['user_id']
        )

    def is_valid_date(self, current_date: datetime) -> bool:
        return self.next_due_date >= current_date


@dataclass
class CreateCategoryDto:
    name: str
    category_type: str
    percentage: int = None

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Self:
        return cls(
            name=data['name'],
            category_type=data['category_type'],
            percentage=int(data['percentage'])
        )


@dataclass
class CategoryDto:
    id: int
    name: str
    category_type: str
    percentage: int = None

    def to_dict(self) -> dict[str, Any]:
        return {
            'id': self.id,
            'name': self.name,
            'category_type': self.category_type,
            'percentage': self.percentage if self.percentage else None,
        }

    @classmethod
    def from_category_entity(cls, category_entity: CategoryEntity) -> Self:
        if isinstance(category_entity, ExpenseCategoryEntity):
            return cls(
                id=category_entity.id,
                name=category_entity.name,
                category_type=category_entity.type_,
                percentage=category_entity.percentage,
            )
        return cls(
            id=category_entity.id,
            name=category_entity.name,
            category_type=category_entity.type_,
        )


@dataclass
class CreateCategorizedBudgetEntryDto:
    category: str
    planned_amount: int
    actual_amount: int

    def to_dict(self) -> dict[str, Any]:
        return {
            "category": self.category,
            "planned_amount": self.planned_amount,
            "actual_amount": self.actual_amount,
            "difference": self.planned_amount - self.actual_amount
        }
