from unittest.mock import patch

import pytest
from werkzeug.exceptions import NotFound


class TestCategoryIdResource:

    @patch('app.service.configuration.category_service.get_by_id')
    def test_get_category_by_id(self, mock_get_by_id, client):
        mock_get_by_id.return_value = {'id': 1, 'name': 'C1'}
        response = client.get('/categories/1')

        assert response.status_code == 200
        assert response.json['name'] == 'C1'
        assert response.json['id'] == 1
        mock_get_by_id.assert_called_once_with(1)

    @patch('app.service.configuration.category_service.get_by_id')
    def test_get_category_by_id_not_found(self, mock_service, client):
        mock_service.side_effect = NotFound('Category not found')
        response = client.get('/categories/2')

        assert response.status_code == 404
        assert response.json == {'message': 'Category not found'}
        mock_service.assert_called_once_with(2)


class TestCategoryNameResource:

    def test_add_category_by_name_invalid_name(self, client):
        response = client.post('/categories/freelance', json={'category_type': 'income'})

        assert response.status_code == 400
        assert response.json['message'] == 'Invalid name'

    def test_add_expense_category_by_name_invalid_category_without_percentage(self, client):
        response = client.post('/categories/Rent', json={'category_type': 'expense'})

        assert response.status_code == 400
        assert response.json['message'] == 'Expense category must have percentage field'

    @patch('app.service.configuration.category_service.get_by_name')
    def test_get_category_by_name(self, mock_get_by_name, client):
        mock_get_by_name.return_value = {'id': 1, 'name': 'Salary', 'category_type': 'income'}
        response = client.get('/categories/Salary')

        assert response.json['id'] == 1
        assert response.json['name'] == 'Salary'
        assert response.json['category_type'] == 'income'
        assert response.status_code == 200
        mock_get_by_name.assert_called_once_with('Salary')

    @patch('app.service.configuration.category_service.get_by_name')
    def test_get_category_by_name_not_found(self, mock_get_by_name, client):
        mock_get_by_name.side_effect = NotFound('Category not found')
        response = client.get('/categories/Salary')

        assert response.status_code == 404
        assert response.json == {'message': 'Category not found'}
        mock_get_by_name.assert_called_once_with('Salary')

    @patch('app.service.configuration.category_service.delete_by_name')
    def test_delete_category_by_name(self, mock_delete_by_name, client):
        mock_delete_by_name.return_value = None
        response = client.delete('/categories/Salary')

        assert response.status_code == 200
        assert response.json == {'message': 'Category deleted'}
        mock_delete_by_name.assert_called_once_with('Salary')

    @patch('app.service.configuration.category_service.delete_by_name')
    def test_delete_category_by_name_not_found(self, mock_delete_by_name, client):
        mock_delete_by_name.side_effect = NotFound('Category not found')
        response = client.delete('/categories/Salary')

        assert response.status_code == 404
        assert response.json == {'message': 'Category not found'}
        mock_delete_by_name.assert_called_once_with('Salary')


class TestChangeExpenseCategoryPercentageResource:

    @patch('app.service.configuration.category_service.update_expense_percentage')
    def test_update_expense_category_percentage(self, mock_update_expense_percentage, client):
        mock_update_expense_percentage.return_value = {
            'id': 1,
            'name': 'Rent',
            'category_type': 'expense',
            'percentage': 30
        }
        response = client.patch('/expense-categories-percentage/1', json={'percentage': 30})

        assert response.status_code == 200
        assert response.json['id'] == 1
        assert response.json['name'] == 'Rent'
        assert response.json['category_type'] == 'expense'
        assert response.json['percentage'] == 30
        mock_update_expense_percentage.assert_called_once_with(1, 30)

    @patch('app.service.configuration.category_service.update_expense_percentage')
    def test_update_expense_category_percentage_not_found(self, mock_update_expense_percentage, client):
        mock_update_expense_percentage.side_effect = NotFound('Category not found')
        response = client.patch('/expense-categories-percentage/1', json={'percentage': 30})

        assert response.status_code == 404
        assert response.json == {'message': 'Category not found'}
        mock_update_expense_percentage.assert_called_once_with(1, 30)

    @patch('app.service.configuration.category_service.update_expense_percentage')
    def test_update_expense_category_percentage_exceeds_sum(self, mock_update_expense_percentage, client):
        mock_update_expense_percentage.side_effect = ValueError('The sum of percentages cannot exceessd 100')
        with pytest.raises(ValueError):
            response = client.patch('/expense-categories-percentage/1', json={'percentage': 70})

            assert response.status_code == 404
            assert response.json['message'] == 'The sum of percentages cannot exceeded'
