import logging
from unittest import mock
from unittest.mock import MagicMock, patch
import pytest
from app.persistent.entity import UserEntity
from app.persistent.configuration import sa
from app.persistent.entity import (
    IncomeEntity,
    ExpenseEntity,
    UserEntity,
    TransactionEntity,
    CategoryEntity,
    ExpenseCategoryEntity,
    IncomeCategoryEntity,
    ActivationTokenEntity
)
# from app.service.configuration import user_service
from app.service.dto import UserDto, CreateUserDto
from app.service.users import UserService, UserSecurityService
from app.config import DB_TEST_URL
from app.main import create_app
from werkzeug.exceptions import NotFound


@pytest.fixture
def client():
    app = create_app()
    app.config.update({
        'TESTING': True
    })

    with app.test_client() as client:
        yield client


@pytest.fixture
def create_user_dto() -> CreateUserDto:
    return CreateUserDto(
        name='U',
        email='u@gmail.com',
        password='****',
        role='admin'
    )


# @pytest.fixture
# def user_data():
#     return {'username': 'u', 'email': 'u@gmail.com', 'password': '***', 'role': 'admin'}


@pytest.fixture
def example_user():
    return {'id': 1, 'name': 'U', 'email': 'xxx@gmail.com', 'password': 'pass1', 'role': 'admin'}


# MagicMock(id=1, username='u', email='u@gmail.com', role='admin')

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


def test_get_user_by_name(user_service, mock_user_repo, example_user):
    mock_user_repo.find_by_name.return_value = MagicMock(
        id=example_user['id'],
        name=example_user['name'],
        password=example_user['password'],
        email=example_user['email'],
        role=example_user['role']
    )

    found_user = user_service.get_by_name('U')
    assert found_user is not None
    assert 'password' not in found_user
    assert found_user['email'] == 'xxx@gmail.com'
    assert found_user['role'] == 'admin'
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

    # @patch('app.service.users.UserService.user_repository')
    # @patch('app.service.users.UserService.activation_token_repository')
    # def test_mock_add_user(mock_activation_token_repo, mock_user_repo, create_user_dto):
    #     mock_user_repo.find_by_name.return_value = MagicMock()
    #     mock_user_repo.find_by_email.return_value = MagicMock()
    #     user_service = UserService(mock_user_repo, mock_activation_token_repo)
    #     user = user_service.add_user(create_user_dto)
    #
    #     assert user['id'] == 1
    #     # assert user.username == 'u'
    #     # assert user.role == 'admin'
    #     # assert mock_user_repo.call_count == 1
    #     # mock_user_repo.assert_called_once_with(create_user_dto)
    #     mock_user_repo.find_by_name.assert_called_with(create_user_dto.name)
    #     mock_user_repo.find_by_email.assert_called_with(create_user_dto.email)

    # @patch('app.service.users.UserService.user_repository')
    # # def test_add_user_email_exists(
    # @patch('app.service.users.UserService.get_by_id',
    #        return_value=MagicMock(id=10, username='u', email='u@gmail.com', role='admin'))
    # def test_get_user_by_id(mock_get, create_user_dto):
    #     result_user = user_service.get_by_id(10)
    #     assert result_user is not None
    #     assert result_user.username == 'u'
    #     assert result_user.email == 'u@gmail.com'
    #     mock_get.assert_called_once_with(10)
    #
    #
    # @patch('app.service.users.UserService.get_by_id',
    #        return_value=None)
    # def test_mock_get_user_by_id_not_found(mock_get, create_user_dto):
    #     result_user = user_service.get_by_id(99)
    #     assert result_user is None
    #     mock_get.assert_called_once_with(99)
