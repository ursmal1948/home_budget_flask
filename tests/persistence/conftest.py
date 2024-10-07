import pytest


@pytest.fixture
def user_data():
    return {
        "name": "Suzy",
        "email": "suzy@gmail.com",
        "password": "suzy123",
    }


@pytest.fixture
def income_data():
    return {
        "amount":10,
        "user_id":1,
        "type_":"income",
        "category_id":"2"
    }
