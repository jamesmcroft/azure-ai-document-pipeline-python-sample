from __future__ import annotations
import json
from shared.validation_result import ValidationResult
from shared.base_request import BaseRequest


class InvoiceBatchRequest(BaseRequest):
    def __init__(self, container_name: str):
        super().__init__()
        self.container_name = container_name

    def validate(self) -> ValidationResult:
        result = ValidationResult()

        if not self.container_name:
            result.add_error("container_name is required")

        return result

    def to_dict(obj: InvoiceBatchRequest) -> dict:
        return {
            "container_name": obj.container_name
        }

    @staticmethod
    def to_json(obj: InvoiceBatchRequest) -> str:
        return json.dumps(obj.to_dict())

    @staticmethod
    def from_json(json_str: str) -> InvoiceBatchRequest:
        return InvoiceBatchRequest.from_dict(json.loads(json_str))

    @staticmethod
    def from_dict(obj: dict) -> InvoiceBatchRequest:
        return InvoiceBatchRequest(
            obj["container_name"]
        )
