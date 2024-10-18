from unittest.mock import MagicMock
import pytest

from app.persistent.entity import UserEntity
from app.service.dto import CreateUserDto
from app.service.users import UserService
from werkzeug.exceptions import NotFound

import flask_praetorian


@pytest.fixture
def create_user_dto() -> CreateUserDto:
    return CreateUserDto(
        name='U',
        email='u@gmail.com',
        password='Examplepass2',
        roles='admin'
    )


@pytest.fixture
def example_user():
    return {'id': 1, 'name': 'U', 'email': 'xxx@gmail.com', 'password': 'Pass1', 'roles': 'admin'}


@pytest.fixture
def mock_user_repo():
    return MagicMock()


@pytest.fixture
def user_service(mock_user_repo):
    return UserService(mock_user_repo)


def test_add_user(user_service, mock_user_repo, create_user_dto):
    mock_user_repo.find_by_name.return_value = None
    mock_user_repo.find_by_email.return_value = None

    added_user = user_service.add_user(create_user_dto)

    assert added_user is not None
    assert added_user['name'] == create_user_dto.name
    assert added_user['email'] == create_user_dto.email
    mock_user_repo.find_by_name.assert_called_once_with(create_user_dto.name)
    mock_user_repo.find_by_email.assert_called_once_with(create_user_dto.email)


def test_get_user_by_id(user_service, mock_user_repo, example_user):
    mock_user_repo.find_by_id.return_value = UserEntity(
        id=example_user['id'],
        name=example_user['name'],
        email=example_user['email'],
        roles=example_user['roles'],
        hashed_password=example_user['password']
    )

    found_user = user_service.get_by_id(1)
    assert found_user is not None
    assert 'password' not in found_user
    assert found_user['name'] == example_user['name']
    assert found_user['email'] == example_user['email']
    assert found_user['roles'] == example_user['roles']
    mock_user_repo.find_by_id.assert_called_once_with(example_user['id'])


def test_get_user_by_name(user_service, mock_user_repo, example_user):
    mock_user_repo.find_by_name.return_value = MagicMock(
        id=example_user['id'],
        name=example_user['name'],
        password=example_user['password'],
        email=example_user['email'],
        roles=example_user['roles']
    )

    found_user = user_service.get_by_name('U')
    assert found_user is not None
    assert 'password' not in found_user
    assert found_user['email'] == example_user['email']
    assert found_user['roles'] == example_user['roles']
    mock_user_repo.find_by_name.assert_called_once_with('U')


def test_get_user_by_email_not_found(user_service, mock_user_repo):
    mock_user_repo.find_by_email.side_effect = NotFound('User not found')

    with pytest.raises(NotFound) as err:
        user_service.get_by_email('exmple-email.com')

    assert str(err.value) == '404 Not Found: User not found'


def test_get_total_income(user_service, mock_user_repo, example_user):
    mock_user_repo.calculate_total_income.return_value = 5000

    total_income = user_service.get_total_income(1)
    assert total_income == 5000


def test_get_total_income_user_not_found(user_service, mock_user_repo):
    mock_user_repo.find_by_id.side_effect = NotFound('User not found')

    with pytest.raises(NotFound) as err:
        user_service.get_total_income(1)

    assert str(err.value) == '404 Not Found: User not found'
