import pytest

from app.persistent.entity import (
    UserEntity,
    IncomeCategoryEntity,
    IncomeEntity
)
from app.persistent.repository import user_repository


@pytest.fixture
def example_user():
    return UserEntity(name='S', password='pass1', email='u@gmail.com', role='admin')


@pytest.fixture
def example_users():
    return [
        UserEntity(name='A', password='P1', email='A@gmail.com', role='admin'),
        UserEntity(name='B', password='P2', email='B@gmail.com', role='user'),

    ]


def test_save_user(app_context, example_user):
    user_repository.save_or_update(example_user)
    user = user_repository.find_by_id(1)

    assert user is not None
    assert user.id == 1


def test_save_many_users(app_context, example_user, example_users):
    users = [example_user] + example_users

    user_repository.save_or_update_many(users)
    saved_users = user_repository.find_all()

    assert saved_users is not None
    assert len(saved_users) == len(users)
    assert saved_users[0].id == 1 and saved_users[0].name == 'S'
    assert saved_users[1].id == 2 and saved_users[1].name == 'A'
    assert saved_users[2].id == 3 and saved_users[2].name == 'B'


def test_update_user(app_context, example_user):
    user_repository.save_or_update(example_user)
    user_from_db = user_repository.find_by_id(1)
    new_name = 'Ursula'
    user_from_db.name = new_name

    new_mail = 'ursula@gmail.com'
    user_from_db.email = new_mail
    user_repository.save_or_update(user_from_db)

    assert user_from_db is not None
    assert user_from_db.name == new_name
    assert user_from_db.email == new_mail
    assert user_from_db.id == 1


def test_find_user_by_id(app_context, example_user):
    user_repository.save_or_update(example_user)
    user_from_db = user_repository.find_by_id(1)

    assert user_from_db is not None
    assert user_from_db.id == 1


def test_find_user_that_does_not_exist(app_context):
    user_from_db = user_repository.find_by_id(999)
    assert user_from_db is None


def test_delete_user_by_id(app_context, example_user):
    user_repository.save_or_update(example_user)
    user_repository.delete_by_id(1)
    user_from_db = user_repository.find_by_id(1)

    assert user_from_db is None


def test_delete_all(app_context, example_user, example_users):
    users = [example_user] + example_users
    user_repository.save_or_update_many(users)

    user_repository.delete_all()
    users_from_db = user_repository.find_all()

    assert len(users_from_db) == 0


def test_find_user_by_email(app_context, example_user):
    user_repository.save_or_update(example_user)
    user_from_db = user_repository.find_by_email(email=example_user.email)

    assert user_from_db is not None
    assert user_from_db.id == 1
    assert user_from_db.name == example_user.name
    assert user_from_db.email == example_user.email
    assert user_from_db.role == example_user.role


def test_find_user_by_name(app_context, example_user):
    user_repository.save_or_update(example_user)
    user_from_db = user_repository.find_by_name(name=example_user.name)

    assert user_from_db is not None
    assert user_from_db.id == 1
    assert user_from_db.name == example_user.name
    assert user_from_db.email == example_user.email
    assert user_from_db.role == example_user.role


def test_calculate_user_total_income(app_context, example_user):
    income_category = IncomeCategoryEntity(name='Salary', type_='income')
    income1 = IncomeEntity(amount=500)
    income2 = IncomeEntity(amount=700)

    income1.user = example_user
    income2.user = example_user
    income_category.income_transactions = [income1, income2]

    user_repository.save_or_update(example_user)
    user_income = user_repository.calculate_total_income(example_user.id)

    assert example_user.id == 1
    assert user_income == income1.amount + income2.amount
