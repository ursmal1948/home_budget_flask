from flask import Flask
from flask_restful import Api
from flask_migrate import Migrate
import logging

from app.security.configuration import configure_security
from app.mail.configuration import MailSender
from app.config import MAIL_SETTINGS, DB_URL, SECURITY_SETTINGS
from app.persistent.configuration import sa
from app.routes.resource import (
    RegisterUserResource,
    ActivationUserResource,
    UserIdResource,
    UserIdTotalIncomeResource,
    CreateUserResource,
    CategoryIdResource,
    CategoryNameResource,
    CreateTransactionResource,
    TransactionIdResource,
    TransactionsFilterResource,
    BudgetSummaryResource,
    BudgetListSummaryResource,
    ProcessRecurringTransactionsResource,
    CreateRecurringTransactionResource,
    TransactionListByCategoryResource,
    ChangeExpenseCategoryPercentageResource,
    RecurringTransactionIdResource
)

logging.basicConfig(level=logging.INFO)


def create_app() -> Flask:
    app = Flask(__name__)
    with app.app_context():
        app.config['SQLALCHEMY_DATABASE_URI'] = DB_URL
        app.config['SQLALCHEMY_ECHO'] = True
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        app.config.update(MAIL_SETTINGS)
        app.config.update(SECURITY_SETTINGS)

        sa.init_app(app)

        configure_security(app)
        MailSender(app, 'ula.malin35@gmail.com')
        migrate = Migrate(app, sa)
        api = Api(app)

        api.add_resource(RegisterUserResource, '/users/register')
        api.add_resource(ActivationUserResource, '/users/activate')
        api.add_resource(UserIdResource, '/users/<int:user_id>')
        api.add_resource(UserIdTotalIncomeResource, '/users/<int:user_id>/total-income')
        api.add_resource(CreateUserResource, '/users')

        api.add_resource(CategoryIdResource, '/categories/<int:category_id>')
        api.add_resource(CategoryNameResource, '/categories/<string:category_name>')
        api.add_resource(ChangeExpenseCategoryPercentageResource, '/expense-categories-percentage/<int:category_id>')

        api.add_resource(CreateTransactionResource, '/transactions')
        api.add_resource(TransactionIdResource, '/transactions/<int:transaction_id>')
        api.add_resource(TransactionListByCategoryResource, '/transactions/<string:category_name>')
        api.add_resource(TransactionsFilterResource, '/transactions/filter')

        api.add_resource(CreateRecurringTransactionResource, '/recurring-transaction')
        api.add_resource(RecurringTransactionIdResource, '/recurring-transactions/<int:transaction_id>')
        api.add_resource(ProcessRecurringTransactionsResource, '/recurring-transactions')

        api.add_resource(BudgetSummaryResource, '/users/budget-summary/<int:user_id>')
        api.add_resource(BudgetListSummaryResource, '/users/budget-summary/')

    return app


if __name__ == '__main__':
    create_app()
