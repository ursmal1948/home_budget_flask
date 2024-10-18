import re


def validate_name(name: str) -> bool:
    if not re.match(r'^[A-Z][a-z]+$', name):
        return False
    return True


user_creation_schema = {
    "type": "object",
    "properties": {
        "name": {
            "type": "string",
            "pattern": r'^[A-Z][a-z]+$'
        },
        "password": {
            "type": "string",
            "pattern": r'^(?=.*[A-Z])(?=.*[a-z])(?=.*\d).{8,}$'
        },
        "email": {
            "type": "string",
            "pattern": r'[\w\.-]+@(gmail.com|wp.pl|onet.pl)$'
        },
        "roles": {
            "type": "string",
        }
    },
    "required": ["name", "password", "email"]
}

category_creation_schema = {
    "type": "object",
    "properties": {
        "category_type": {"type": "string", "enum": ["income", "expense"]},
        "percentage": {"type": "integer", "minimum": 1, "maximum": 100},
    },
    "required": ["category_type"]
}

transaction_creation_schema = {
    "type": "object",
    "properties": {
        "amount": {"type": "integer", "minimum": 10},
        "user_id": {"type": "integer"},
        "category_id": {"type": "integer"}
    },
    "required": ["amount", "user_id", "category_id"]
}
transaction_type_schema = {
    "type": "object",
    "properties": {
        "type": {"type": "string", "enum": ["INCOME", "EXPENSE"]},
    }
}

amount_schema = {
    "type": "object",
    "properties": {
        "amount": {"type": "integer", "minimum": 10}
    },
    "required": ["amount"]
}

percentage_schema = {
    "type": "object",
    "properties": {
        "percentage": {"type": "integer", "minimum": 1, "maximum": 100},
    },
    "required": ["percentage"]
}

recurring_transaction_creation_schema = {
    "type": "object",
    "properties": {
        "amount": {"type": "integer", "minimum": 10},
        "frequency": {"type": "string", "enum": ["DAILY", "WEEKLY", "MONTHLY"]},
        "next_due_date": {"type": "string", "format": "date", "pattern": r'^\d{4}-\d{2}-\d{2}$'},
        "category_id": {"type": "integer"},
        "user_id": {"type": "integer"},

    },
    "required": ["amount", "frequency", "next_due_date", "category_id", "user_id"]
}
recurring_transction_update_schema = {
    "type": "object",
    "properties": {
        "amount": {"type": "integer", "minimum": 10},
        "frequency": {"type": "string", "enum": ["DAILY", "WEEKLY", "MONTHLY"]},
        "next_due_date": {"type": "string", "format": "date", "pattern": r'^\d{4}-\d{2}-\d{2}$'},
    }
}
