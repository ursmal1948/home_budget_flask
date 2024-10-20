import flask_praetorian
from flask_restful import Resource
from flask import request, Response
from jsonschema import validate
import logging

from app.service.dto import (
    RegisterUserDto,
    CreateUserDto,
    CreateCategoryDto,
    CreateTransactionDto,
    CreateRecurringTransactionDto,

)
from app.routes.schemas import (
    validate_name,
    user_creation_schema,
    category_creation_schema,
    transaction_creation_schema,
    amount_schema,
    percentage_schema,
    recurring_transction_update_schema,
    recurring_transaction_creation_schema
)
from app.service.configuration import (
    user_service,
    user_security_service,
    category_service,
    transaction_service,
    budget_planning_service,
    recurring_transaction_service
)

logging.basicConfig(level=logging.INFO)


class RegisterUserResource(Resource):

    def post(self) -> Response:
        json_body = request.json
        validate(json_body, schema=user_creation_schema)
        register_user_dto = RegisterUserDto.from_dict(json_body)
        return user_security_service.register_user(register_user_dto)


class ActivationUserResource(Resource):

    def post(self) -> Response:
        token = request.json['token']
        return user_security_service.activate_user(token)


class CreateUserResource(Resource):

    def post(self) -> Response:
        json_body = request.json
        validate(json_body, schema=user_creation_schema)
        user_dto = CreateUserDto.from_dict(json_body)

        return user_service.add_user(user_dto)


class UserIdResource(Resource):
    # @flask_praetorian.auth_required
    def get(self, user_id: int) -> Response:
        return user_service.get_by_id(user_id)


class UserIdTotalIncomeResource(Resource):
    # @flask_praetorian.auth_required
    def get(self, user_id: int) -> Response:
        return user_service.get_total_income(user_id)


class CategoryIdResource(Resource):

    # @flask_praetorian.auth_required
    def get(self, category_id: int) -> Response:
        return category_service.get_by_id(category_id)


class CategoryNameResource(Resource):
    # @flask_praetorian.auth_required
    def get(self, category_name: str) -> Response:
        return category_service.get_by_name(category_name)

    # @flask_praetorian.roles_required('admin')
    def post(self, category_name: str) -> Response:
        if not validate_name(category_name):
            return {'message': 'Invalid name'}, 400

        json_body = request.json
        validate(json_body, schema=category_creation_schema)
        category_type = json_body['category_type']
        percentage = json_body.get('percentage', None)

        if category_type == 'expense' and percentage is None:
            return {'message': 'Expense category must have percentage field'}, 400

        category_dto = CreateCategoryDto(
            name=category_name,
            category_type=category_type,
            percentage=percentage
        )
        return category_service.add_category(category_dto)

    # @flask_praetorian.roles_required('admin')
    def delete(self, category_name: str) -> Response:
        category_service.delete_by_name(category_name)
        return {'message': 'Category deleted'}, 200


class ChangeExpenseCategoryPercentageResource(Resource):
    # @flask_praetorian.roles_required('admin')
    def patch(self, category_id: int):
        json_body = request.json
        validate(json_body, schema=percentage_schema)
        new_percentage = json_body['percentage']

        return category_service.update_expense_percentage(category_id, new_percentage)


class CreateTransactionResource(Resource):
    # @flask_praetorian.auth_required
    def post(self) -> Response:
        json_body = request.json
        validate(json_body, schema=transaction_creation_schema)

        transaction_dto = CreateTransactionDto.from_dict(json_body)
        return transaction_service.add_transaction(transaction_dto)


class TransactionIdResource(Resource):
    # @flask_praetorian.auth_required
    def get(self, transaction_id: int) -> Response:
        return transaction_service.get_by_id(transaction_id)

    # @flask_praetorian.auth_required
    def patch(self, transaction_id: int) -> Response:
        json_body = request.json
        validate(json_body, amount_schema)
        new_amount = json_body['amount']

        return transaction_service.update_transaction_amount(transaction_id, new_amount)


class TransactionListByCategoryResource(Resource):
    # @flask_praetorian.roles_required('admin')
    def get(self, category_name: str) -> Response:
        return transaction_service.get_all_transactions_for_category(category_name)


class TransactionsFilterResource(Resource):
    # @flask_praetorian.roles_required('admin')
    def get(self) -> Response:
        amount = int(request.args.get('amount'))
        json_body = request.json
        transaction_type = json_body['transaction_type']

        if transaction_type not in ['INCOME', 'EXPENSE']:
            return {'message': 'Invalid transaction type'}, 400

        return transaction_service.get_transactions_higher_than(amount, transaction_type)


class BudgetSummaryResource(Resource):
    # @flask_praetorian.auth_required
    def get(self, user_id: int) -> Response:
        return budget_planning_service.generate_budget_entries_for_user(user_id)


class BudgetListSummaryResource(Resource):
    # @flask_praetorian.roles_required('admin')
    def get(self) -> Response:
        return budget_planning_service.generate_budget_entries_for_all_users()


class CreateRecurringTransactionResource(Resource):
    # @flask_praetorian.auth_required
    def post(self) -> Response:
        json_body = request.json
        validate(json_body, schema=recurring_transaction_creation_schema)
        recurring_transaction_dto = CreateRecurringTransactionDto.from_dict(data=json_body)
        return recurring_transaction_service.add_recurring_transaction(recurring_transaction_dto)


class RecurringTransactionIdResource(Resource):

    # @flask_praetorian.auth_required
    def get(self, transaction_id: int) -> Response:
        return recurring_transaction_service.get_by_id(transaction_id)

    # @flask_praetorian.auth_required
    def patch(self, transaction_id: int) -> Response:
        json_body = request.json
        if not json_body:
            return {'message': 'No information to update'}, 400

        validate(json_body, schema=recurring_transction_update_schema)
        return recurring_transaction_service.update_recurring_transaction(transaction_id, **json_body)


class ProcessRecurringTransactionsResource(Resource):

    # @flask_praetorian.roles_required('admin')
    def post(self) -> Response:
        recurring_transactions = recurring_transaction_service.process_recurring_transactions()
        if not recurring_transactions:
            return {'message': 'No recurring transactions to process'}, 200

        return recurring_transactions
