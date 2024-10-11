from unittest.mock import patch
import pytest
from werkzeug.exceptions import NotFound
from jsonschema.exceptions import ValidationError
from app.service.dto import CreateTransactionDto


class TestCreateTransactionResource:

    @patch('app.service.configuration.transaction_service.add_transaction')
    def test_add_transaction(self, mock_add_transaction, client, transaction_data):
        mock_add_transaction.return_value = {'id': 3,
                                             "amount": transaction_data["amount"],
                                             "user_id": transaction_data["user_id"],
                                             "category_id": transaction_data["category_id"],
                                             "type": "income"
                                             }
        response = client.post('/transactions', json=transaction_data)
        dto = CreateTransactionDto(**transaction_data)

        assert response.status_code == 200
        assert response.json['id'] == 3
        assert response.json['amount'] == transaction_data["amount"]
        assert response.json['type'] == 'income'
        mock_add_transaction.assert_called_once_with(dto)


class TestTransactionIdResource:

    @patch('app.service.configuration.transaction_service.get_by_id')
    def test_get_transaction_by_id(self, mock_get_by_id, client, transaction_data):
        mock_get_by_id.return_value = {'id': 1,
                                       'amount': transaction_data["amount"],
                                       'user_id': transaction_data["user_id"],
                                       'category_id': transaction_data["category_id"],
                                       'type': 'income'
                                       }
        response = client.get('/transactions/1')

        assert response.status_code == 200
        assert response.json['id'] == 1
        assert response.json['amount'] == transaction_data["amount"]
        assert response.json['type'] == 'income'
        mock_get_by_id.assert_called_once_with(1)

    @patch('app.service.configuration.transaction_service.get_by_id')
    def test_get_transaction_by_id_not_found(self, mock_get_by_id, client, transaction_data):
        mock_get_by_id.side_effect = NotFound('Transaction not found')
        response = client.get('/transactions/1')

        assert response.status_code == 404
        assert response.json['message'] == 'Transaction not found'
        mock_get_by_id.assert_called_once_with(1)

    @patch('app.service.configuration.transaction_service.update_transaction_amount')
    def test_update_transaction(self, mock_update_transaction_amount, client, transaction_data):
        new_amount = 3000
        mock_update_transaction_amount.return_value = {'id': 3,
                                                       'amount': new_amount,
                                                       'user_id': transaction_data["user_id"],
                                                       'category_id': transaction_data["category_id"],
                                                       'type': 'income'
                                                       }
        response = client.patch('/transactions/1', json={'amount': new_amount})

        assert response.status_code == 200
        assert response.json['amount'] == new_amount
        mock_update_transaction_amount.assert_called_once_with(1, new_amount)

    def test_update_transaction_too_small_amount(self, client, transaction_data):
        new_amount = 5
        with pytest.raises(ValidationError) as err:
            client.patch('/transactions/1', json={'amount': new_amount})

        assert f'{new_amount} is less than the minimum of 10' in str(err.value)


class TestTransactionListByCategoryResource:

    @patch('app.service.configuration.transaction_service.get_all_transactions_for_category')
    def test_get_all_transactions_for_category(self, mock_all_transactions_for_category, client):
        category_name = 'Salary'
        mock_all_transactions_for_category.return_value = [
            {
                "id": 1,
                "amount": 100,
                "user_id": 1,
                "category_id": 1,
                "type": "income"
            },
            {
                "id": 2,
                "amount": 50,
                "user_id": 1,
                "category_id": 1,
                "type": "income"
            }
        ]

        response = client.get(f'/transactions/{category_name}')

        assert response.status_code == 200
        assert len(response.json) == 2
        assert response.json[0]['id'] == 1
        assert response.json[1]['id'] == 2
        mock_all_transactions_for_category.assert_called_once_with(category_name)

    @patch('app.service.configuration.transaction_service.get_all_transactions_for_category')
    def test_get_all_transactions_for_category_empty_transactions_list(self, mock_all_transactions_for_category,
                                                                       client):
        category_name = 'Salary'
        mock_all_transactions_for_category.return_value = []

        response = client.get(f'/transactions/{category_name}')

        assert response.status_code == 200
        assert len(response.json) == 0
        mock_all_transactions_for_category.assert_called_once_with(category_name)

    @patch('app.service.configuration.transaction_service.get_all_transactions_for_category')
    def test_get_all_transactions_for_category_not_found(self, mock_all_transactions_for_category, client):
        mock_all_transactions_for_category.side_effect = NotFound('Category not found')
        category_name = 'Rent'
        response = client.get(f'/transactions/{category_name}')

        assert response.status_code == 404
        assert response.json['message'] == 'Category not found'
        mock_all_transactions_for_category.assert_called_once_with(category_name)


class TestTransactionsFilterResource:

    @patch('app.service.configuration.transaction_service.get_transactions_higher_than')
    def test_get_transactions_higher_than(self, mock_filter, client):
        greater_than_amount = 300
        transaction_type = 'INCOME'
        mock_filter.return_value = [
            {
                "id": 3,
                "amount": 700,
                "user_id": 1,
                "category_id": 3,
                "type": "income"
            },
            {
                "id": 4,
                "amount": 800,
                "user_id": 2,
                "category_id": 2,
                "type": "income"
            }
        ]

        response = client.get(f'transactions/filter?amount={greater_than_amount}',
                              json={'transaction_type': transaction_type})

        assert response.status_code == 200
        assert len(response.json) == 2
        assert response.json[0]['id'] == 3 and response.json[1]['id'] == 4
        assert response.json[0]['amount'] and response.json[1]['amount'] > greater_than_amount
        mock_filter.assert_called_once_with(greater_than_amount, transaction_type)

    def test_get_transactions_higher_than_incorrect_transaction_type(self, client):
        response = client.get('transactions/filter?amount=500',
                              json={'transaction_type': 'SOME TYPE'})

        assert response.status_code == 400
        assert response.json['message'] == 'Invalid transaction type'
