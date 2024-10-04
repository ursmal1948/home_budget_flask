import pytest
@pytest.fixture
def user_data():
    return {
        "name":"Suzy",
        "email":"suzy@gmail.com",
        "password":"suzy123",
    }