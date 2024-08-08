from __future__ import annotations
import json


class ValidationResult:
    def __init__(self):
        self.is_valid = True
        self.messages = []

    def add_message(self, message: str):
        self.messages.append(message)

    def add_error(self, message: str):
        self.is_valid = False
        self.messages.append(message)

    def merge(self, result: 'ValidationResult'):
        self.is_valid = self.is_valid and result.is_valid
        self.messages.extend(result.messages)

    def to_str(self):
        return ", ".join(self.messages)

    def to_dict(self) -> dict:
        return {
            "is_valid": self.is_valid,
            "messages": self.messages
        }

    @staticmethod
    def to_json(obj: ValidationResult) -> str:
        return json.dumps(obj.to_dict())

    @staticmethod
    def from_json(json_str: str) -> ValidationResult:
        return ValidationResult.from_dict(json.loads(json_str))

    @staticmethod
    def from_dict(obj: dict) -> ValidationResult:
        result = ValidationResult()
        result.is_valid = obj["is_valid"]
        result.messages = obj["messages"]
        return result
