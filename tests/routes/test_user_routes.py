import logging
from unittest.mock import patch
from werkzeug.exceptions import NotFound

logging.basicConfig(level=logging.INFO)


class TestUserRoutes:

    @patch('app.routes.resource.CreateUserResource.post')
    def test_create_user_route(self, mock_get, client, user_data):
        mock_response = {
            'id': 1,
            'name': user_data['name'],
            'email': user_data['email'],
            'password': user_data['password'],
            'role': user_data['role']
        }
        mock_get.return_value = mock_response
        response = client.post('/users', json=user_data)
        assert response.json == mock_response
        assert response.status_code == 200

    @patch('app.routes.resource.UserIdResource.get')
    def test_get_user_by_id_route(self, mock_get, client, user_data):
        mock_response = {
            'id': 1,
            'name': user_data['name'],
            'email': user_data['email'],
            'password': user_data['password'],
            'role': user_data['role']
        }
        mock_get.return_value = mock_response

        response = client.get('/users/1', json=user_data)
        assert response.json == mock_response
        assert response.status_code == 200

    @patch('app.routes.resource.UserIdResource.get')
    def test_get_user_by_id_not_found(self, mock_get, client):
        mock_get.side_effect = NotFound('User not found')
        response = client.get('/users/999')

        assert response.status_code == 404
        assert response.json == {'message': 'User not found'}
