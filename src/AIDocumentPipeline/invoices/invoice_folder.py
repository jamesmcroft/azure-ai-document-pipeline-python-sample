from __future__ import annotations
import json
from shared.validation_result import ValidationResult
from shared.base_request import BaseRequest


class InvoiceFolder(BaseRequest):
    def __init__(self, container_name: str, name: str, invoice_file_names: list[str]):
        super().__init__()
        self.container_name = container_name
        self.name = name
        self.invoice_file_names = invoice_file_names

    def validate(self) -> ValidationResult:
        result = ValidationResult()

        if not self.container_name:
            result.add_error("container_name is required")

        if not self.name:
            result.add_error("name is required")

        if not self.invoice_file_names or len(self.invoice_file_names) == 0:
            result.add_error("invoice_file_names is required")

        return result

    def to_dict(obj: InvoiceFolder) -> dict:
        return {
            "container_name": obj.container_name,
            "name": obj.name,
            "invoice_file_names": obj.invoice_file_names
        }

    @staticmethod
    def to_json(obj: InvoiceFolder) -> str:
        return json.dumps(obj.to_dict())

    @staticmethod
    def from_json(json_str: str) -> InvoiceFolder:
        return InvoiceFolder.from_dict(json.loads(json_str))

    @staticmethod
    def from_dict(obj: dict) -> InvoiceFolder:
        result = InvoiceFolder(
            obj["container_name"],
            obj["name"],
            obj["invoice_file_names"]
        )
        return result
