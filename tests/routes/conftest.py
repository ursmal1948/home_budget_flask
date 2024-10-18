import pytest
from app.main import create_app


@pytest.fixture
def client():
    app = create_app()
    app.config['TESTING'] = True

    with app.test_client() as client:
        yield client


@pytest.fixture
def transaction_data():
    return {
        "amount": 700,
        "user_id": 1,
        "category_id": 3
    }


@pytest.fixture
def user_data():
    return {
        'name': 'Ula',
        'email': 'u@gmail.com',
        'password': 'Password123*',
        'roles': 'ADMIN'
    }
