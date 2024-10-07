from app.persistent.entity import UserEntity, IncomeEntity, TransactionEntity


def test_when_user_is_created_correctly(user_data):
    user = UserEntity(**user_data)
    assert user is not None
    assert isinstance(user, UserEntity)
    assert ((user_data['name'], user_data['email'], user_data['password'])
            == (user.name, user.email, user.password))


def test_user_to_dict(user_data):
    user = UserEntity(**user_data)
    user_to_dict = user.to_dict()
    assert (user_to_dict['name'], user_to_dict['email'], user_to_dict['password']) == (
        user.name, user.email, user.password
    )


def test_when_income_is_created_correctly(income_data):
    income = IncomeEntity(**income_data)
    assert income is not None
    assert isinstance(income, TransactionEntity) and isinstance(income, IncomeEntity)
    assert not income.id
    assert income.type_ == 'income'
    assert income.amount == income_data['amount']
    assert income.user_id == income_data['user_id']
