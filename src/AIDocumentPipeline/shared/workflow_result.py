from __future__ import annotations
import json
from shared.validation_result import ValidationResult
import logging


class WorkflowResult(ValidationResult):
    activity_results: list[WorkflowResult]

    def __init__(self, name: str):
        super().__init__()
        self.name = name
        self.activity_results = []

    def add_message(self, action: str, message: str):
        log = f"{self.name}::{action} - {message}"
        logging.info(log)
        super().add_message(log)

    def add_error(self, action: str, message: str):
        log = f"{self.name}::{action} - {message}"
        logging.error(log)
        super().add_error(log)

    def add_activity_result(self, action: str, message: str, result: WorkflowResult):
        self.activity_results.append(result)
        log = f"{self.name}::{action} - {message}"
        logging.info(log)

    def to_dict(obj: WorkflowResult) -> dict:
        return {
            "is_valid": obj.is_valid,
            "messages": obj.messages,
            "activity_results": [WorkflowResult.to_dict(r) for r in obj.activity_results]
        }

    @staticmethod
    def to_json(obj: WorkflowResult) -> str:
        return json.dumps(obj.to_dict())

    @staticmethod
    def from_json(json_str: str) -> WorkflowResult:
        return WorkflowResult.from_dict(json.loads(json_str))

    @staticmethod
    def from_dict(obj: dict) -> WorkflowResult:
        result = WorkflowResult(obj["name"])
        result.is_valid = obj["is_valid"]
        result.messages = obj["messages"]
        result.activity_results = [WorkflowResult.from_dict(
            r) for r in obj["activity_results"]]
        return result
