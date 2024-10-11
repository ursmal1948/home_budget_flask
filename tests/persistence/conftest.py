import pytest
from flask import Flask
from app.persistent.configuration import sa


@pytest.fixture
def app_context():
    app = Flask(__name__)
    with app.app_context():
        app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///memory"
        app.config['TESTING'] = True
        sa.init_app(app)

        sa.create_all()

        yield

        sa.drop_all()


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
        "amount": 10,
        "user_id": 1,
        "type_": "income",
        "category_id": "2"
    }
