# import logging
# from unittest import mock
# from unittest.mock import MagicMock, patch
# import pytest
# from app.persistent.entity import UserEntity
# from app.persistent.configuration import sa
# from app.persistent.entity import (
#     IncomeEntity,
#     ExpenseEntity,
#     UserEntity,
#     TransactionEntity,
#     CategoryEntity,
#     ExpenseCategoryEntity,
#     IncomeCategoryEntity,
#     ActivationTokenEntity
# )
# from app.service.configuration import user_service
# from app.service.dto import UserDto, CreateUserDto
# from app.service.users import UserService
# from app.config import DB_TEST_URL
# from app.main import create_app
#
#
# @pytest.fixture
# def client():
#     app = create_app()
#     app.config.update({
#         'TESTING': True,
#         'SQLALCHEMY_DATABASE_URI': DB_TEST_URL
#     })
#
#     with app.test_client() as client:
#         yield client
#
#
# @pytest.fixture
# def create_user_dto() -> CreateUserDto:
#     return CreateUserDto(
#         name='U',
#         email='u@gmail.com',
#         password='****',
#         role='admin'
#     )
#
#
# # testowanie serwis z wykorzystaniem MOCKOWANIA.
# @pytest.fixture
# def user_data():
#     return {'username': 'u', 'email': 'u@gmail.com', 'password': '***', 'role': 'admin'}
#
#
# @patch('app.service.users.UserService.add_user',
#        return_value=MagicMock(id=1, username='u', email='u@gmail.com', role='admin'))
# def test_mock_add_user(mock_add, create_user_dto):
#     user = user_service.add_user(create_user_dto)
#     assert user.id == 1
#     assert user.username == 'u'
#     assert user.role == 'admin'
#     assert mock_add.call_count == 1
#     mock_add.assert_called_once_with(create_user_dto)
#
#
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
