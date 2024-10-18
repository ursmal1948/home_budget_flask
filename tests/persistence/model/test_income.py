from app.persistent.entity import IncomeEntity, TransactionEntity


def test_when_income_is_created_correctly(income_data):
    income = IncomeEntity(**income_data)
    assert income is not None
    assert isinstance(income, TransactionEntity) and isinstance(income, IncomeEntity)
    assert not income.id
    assert income.type_ == 'income'
    assert income.amount == income_data['amount']
    assert income.user_id == income_data['user_id']
