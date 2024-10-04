from flask_restful import Resource, Api, reqparse
from flask import jsonify, request, Response
from app.service.dto import (
    RegisterUserDto,
    UserDto,
    CreateUserDto,
    CreateCategoryDto,
    CreateTransactionDto,
    TransactionDto,
    CreateRecurringTransactionDto,

)
from app.routes.schemas import (
    validate_name,
    category_creation_schema,
    transaction_creation_schema,
    transaction_type_schema
)
from app.service.configuration import (
    user_service,
    category_service,
    transaction_service,
    budget_planning_service,
    recurring_transaction_service
)
from jsonschema import validate

import logging

logging.basicConfig(level=logging.INFO)


class RegisterUserResource(Resource):

    def post(self) -> Response:
        register_user_dto = RegisterUserDto.from_dict(request.json)
        return user_service.register_user(register_user_dto)


class ActivationUserResource(Resource):

    def post(self) -> Response:
        token = request.json['token']
        return user_service.activate_user(token)


class CreateUserResource(Resource):

    def post(self) -> Response:
        data = request.json
        name = data['name']
        if not validate_name(name):
            return {'message': 'Invalid name'}, 400

        user_dto = CreateUserDto.from_dict(data)
        return user_service.add_user(user_dto)


class UserIdResource(Resource):

    def get(self, user_id: int) -> Response:
        return user_service.get_by_id(user_id)


class CategoryNameResource(Resource):
    def get(self, category_name: str) -> Response:
        return category_service.get_by_name(category_name)

    def post(self, category_name: str) -> Response:
        if not validate_name(category_name):
            return jsonify({'message': 'Invalid name'}), 400

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

    def delete(self, category_name: str) -> Response:
        category_service.delete_by_name(category_name)
        return {'message': 'Category deleted'}, 200


class TransactionResource(Resource):
    def post(self) -> Response:
        json_body = request.json
        validate(json_body, schema=transaction_creation_schema)

        transaction_dto = CreateTransactionDto.from_dict(json_body)
        return transaction_service.add_transaction(transaction_dto)


class BudgetSummaryResource(Resource):
    def post(self, user_id: int) -> Response:
        return budget_planning_service.generate_budget_entries(user_id)


class CreateRecurringTransaction(Resource):
    def post(self) -> Response:
        json_body = request.json
        recurring_transaction_dto = CreateRecurringTransactionDto.from_dict(data=json_body)

        recurring_transaction = recurring_transaction_service.create_recurring_transaction(recurring_transaction_dto)
        return {'recurring_transaction': recurring_transaction.to_dict()}, 201


class ProcessRecurringTransactionsResource(Resource):
    def post(self) -> Response:
        recurring_transactions = recurring_transaction_service.process_recurring_transactions()
        if not recurring_transactions:
            return {'message': 'No recurring transactions to process'}, 200
        return recurring_transactions


class TransactionsFilterResource(Resource):
    def get(self) -> Response:
        amount = request.args.get('amount')
        json_body = request.json
        transaction_type = json_body['transaction_type']
        validate(json_body, schema=transaction_type_schema)
        return transaction_service.get_higher_than(amount, transaction_type)
