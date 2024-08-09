from __future__ import annotations
import json
from shared.validation_result import ValidationResult
import logging


class WorkflowResult(ValidationResult):
    """Defines the result of a workflow operation (orchestration or activity), containing a list of activity results in addition to the validation messages."""

    activity_results: list[WorkflowResult]

    def __init__(self, name: str):
        """Initializes a new instance of the WorkflowResult class.

        :param name: The name of the workflow operation.
        """

        super().__init__()
        self.name = name
        self.activity_results = []

    def add_message(self, action: str, message: str):
        """Adds a structured message to the list of messages without changing the `is_valid` flag.

        :param action: The action that generated the message, e.g. a function name.
        :param message: The message to add.
        """

        log = f"{self.name}::{action} - {message}"
        logging.info(log)
        super().add_message(log)

    def add_error(self, action: str, message: str):
        """Adds a structured error message to the list of messages and sets the `is_valid` flag to `False`.

        :param action: The action that generated the error message, e.g. a function name.
        :param message: The error message to add.
        """

        log = f"{self.name}::{action} - {message}"
        logging.error(log)
        super().add_error(log)

    def add_activity_result(self, action: str, message: str, result: WorkflowResult):
        """Adds an activity result to the list of activity results, and logs a message.

        :param action: The action that generated the result, e.g. a function name.
        :param message: The message to log.
        :param result: The `WorkflowResult` instance to add as an activity result.
        """

        self.activity_results.append(result)
        log = f"{self.name}::{action} - {message}"
        logging.info(log)

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "activity_results": [r.to_dict() for r in self.activity_results],
            "is_valid": self.is_valid,
            "messages": self.messages
        }

    @staticmethod
    def to_json(obj: WorkflowResult) -> str:
        """Converts the object instance to a JSON string. Required for serialization in Azure Functions when passing the result between functions.

        :param obj: The object instance to convert.
        :return: A JSON string representing the object instance.
        """

        return json.dumps(obj.to_dict())

    @staticmethod
    def from_json(json_str: str) -> WorkflowResult:
        """Converts a JSON string to the object instance. Required for deserialization in Azure Functions when receiving the result from another function.

        :param json_str: The JSON string to convert.
        :return: A object instance created from the JSON string.
        """

        return WorkflowResult.from_dict(json.loads(json_str))

    @staticmethod
    def from_dict(obj: dict) -> WorkflowResult:
        """Converts a dictionary to an object instance.

        :param obj: The dictionary to convert.
        :return: A object instance created from the dictionary.
        """

        result = WorkflowResult(obj["name"])
        result.is_valid = obj["is_valid"]
        result.messages = obj["messages"]
        result.activity_results = [WorkflowResult.from_dict(
            r) for r in obj["activity_results"]]
        return result
