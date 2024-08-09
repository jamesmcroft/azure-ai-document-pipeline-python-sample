from __future__ import annotations
import json
from shared.validation_result import ValidationResult
from shared.base_request import BaseRequest


class InvoiceFolder(BaseRequest):
    """Defines a model for grouping a set of invoice files by their containing folder."""

    def __init__(self, container_name: str, name: str, invoice_file_names: list[str]):
        """Initializes a new instance of the InvoiceFolder class.

        :param container_name: The name of the Azure Blob Storage container containing the invoice files.
        :param name: The name of the folder containing the invoice files.
        :param invoice_file_names: A list of the blob names of the invoice files in the container.
        """

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

    def to_dict(self) -> dict:
        """Returns a dictionary representation of the object."""

        return {
            "container_name": self.container_name,
            "name": self.name,
            "invoice_file_names": self.invoice_file_names
        }

    @staticmethod
    def to_json(obj: InvoiceFolder) -> str:
        """Converts the object instance to a JSON string. Required for serialization in Azure Functions when passing the result between functions.

        :param obj: The object instance to convert.
        :return: A JSON string representing the object instance.
        """

        return json.dumps(obj.to_dict())

    @staticmethod
    def from_json(json_str: str) -> InvoiceFolder:
        """Converts a JSON string to the object instance. Required for deserialization in Azure Functions when receiving the result from another function.

        :param json_str: The JSON string to convert.
        :return: A object instance created from the JSON string.
        """

        return InvoiceFolder.from_dict(json.loads(json_str))

    @staticmethod
    def from_dict(obj: dict) -> InvoiceFolder:
        """Converts a dictionary to an object instance.

        :param obj: The dictionary to convert.
        :return: A object instance created from the dictionary.
        """

        result = InvoiceFolder(
            obj["container_name"],
            obj["name"],
            obj["invoice_file_names"]
        )
        return result
