import re


def validate_name(name: str) -> bool:
    if not re.match(r'^[A-Z][a-z]+$', name):
        return False
    return True


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
