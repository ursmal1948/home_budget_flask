import logging
from unittest.mock import patch, MagicMock
from werkzeug.exceptions import NotFound

logging.basicConfig(level=logging.INFO)


class TestCreateUserResource:
    @patch('app.service.configuration.user_service.add_user')
    def test_add_user(self, mock_add_user, client, user_data):
        mock_response = {
            'id': 1,
            'name': user_data['name'],
            'email': user_data['email'],
            'password': user_data['password'],
            'role': user_data['role']
        }
        mock_add_user.return_value = mock_response
        response = client.post('/users', json=user_data)
        assert response.json == mock_response
        assert response.status_code == 200


class TestUserIdResource:

    @patch('app.service.configuration.user_service.get_by_id')
    def test_get_user_by_id(self, mock_get_by_id, client, user_data):
        mock_response = {
            'id': 1,
            'name': user_data['name'],
            'email': user_data['email'],
            'password': user_data['password'],
            'role': user_data['role']
        }
        mock_get_by_id.return_value = mock_response

        response = client.get('/users/1', json=user_data)
        assert response.json == mock_response
        assert response.status_code == 200

    @patch('app.service.configuration.user_service.get_by_id')
    def test_get_user_by_id_not_found(self, mock_get_by_id, client):
        mock_get_by_id.side_effect = NotFound('User not found')
        response = client.get('/users/1')

        assert response.status_code == 404
        assert response.json == {'message': 'User not found'}
        mock_get_by_id.assert_called_once_with(1)


class TestUserIdTotalIncomeResource:
    @patch('app.service.configuration.user_service.get_total_income')
    def test_get_user_total_income(self, mock_get_total_income, client):
        mock_get_total_income.return_value = 1000
        response = client.get('/users/1/total-income')

        assert response.status_code == 200
        assert response.json == 1000
