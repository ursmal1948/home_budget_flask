import pytest
from app.main import create_app
from app.config import DB_TEST_URL
from app.main import create_app


@pytest.fixture
def client():
    app = create_app()
    app.config.update({
        'TESTING': True,
        'SQLALCHEMY_DATABASE_URI': DB_TEST_URL
    })

    with app.test_client() as client:
        yield client


@pytest.fixture
def user_data():
    return {
        'name': 'Ula',
        'email': 'u@gmail.com',
        'password': '****',
        'role': 'admin'
    }
