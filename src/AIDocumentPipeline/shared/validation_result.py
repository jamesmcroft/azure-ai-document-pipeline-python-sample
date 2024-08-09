from __future__ import annotations
import json


class ValidationResult:
    """Defines the result of a validation operation, containing a list of messages and a flag indicating if the validation was successful."""

    def __init__(self):
        """Initializes a new instance of the ValidationResult class with an empty list of messages and the `is_valid` flag set to `True`."""

        self.is_valid = True
        self.messages = []

    def add_message(self, message: str):
        """Adds a message to the list of messages without changing the `is_valid` flag.

        :param message: The message to add.
        """

        self.messages.append(message)

    def add_error(self, message: str):
        """Adds an error message to the list of messages and sets the `is_valid` flag to `False`.

        :param message: The error message to add.
        """

        self.is_valid = False
        self.messages.append(message)

    def merge(self, result: ValidationResult):
        """Merges the messages of another `ValidationResult` instance into the current instance and updates the `is_valid` flag accordingly.

        :param result: The `ValidationResult` instance to merge.
        """

        self.is_valid = self.is_valid and result.is_valid
        self.messages.extend(result.messages)

    def to_str(self):
        """Returns a string representation of the validation result messages as a comma-separated list."""

        return ", ".join(self.messages)

    def to_dict(self) -> dict:
        """Returns a dictionary representation of the object."""

        return {
            "is_valid": self.is_valid,
            "messages": self.messages
        }

    @staticmethod
    def to_json(obj: ValidationResult) -> str:
        """Converts the object instance to a JSON string. Required for serialization in Azure Functions when passing the result between functions.

        :param obj: The object instance to convert.
        :return: A JSON string representing the object instance.
        """

        return json.dumps(obj.to_dict())

    @staticmethod
    def from_json(json_str: str) -> ValidationResult:
        """Converts a JSON string to the object instance. Required for deserialization in Azure Functions when receiving the result from another function.

        :param json_str: The JSON string to convert.
        :return: A object instance created from the JSON string.
        """

        return ValidationResult.from_dict(json.loads(json_str))

    @staticmethod
    def from_dict(obj: dict) -> ValidationResult:
        """Converts a dictionary to an object instance.

        :param obj: The dictionary to convert.
        :return: A object instance created from the dictionary.
        """

        result = ValidationResult()
        result.is_valid = obj["is_valid"]
        result.messages = obj["messages"]
        return result
