from __future__ import annotations
import json
from shared.validation_result import ValidationResult
from shared.base_request import BaseRequest


class InvoiceBatchRequest(BaseRequest):
    """Defines a request to process a batch of invoices in a Storage container."""

    def __init__(self, container_name: str):
        """Initializes a new instance of the InvoiceBatchRequest class.

        :param container_name: The name of the Azure Blob Storage container containing the invoice folders.
        """

        super().__init__()
        self.container_name = container_name

    def validate(self) -> ValidationResult:
        result = ValidationResult()

        if not self.container_name:
            result.add_error("container_name is required")

        return result

    def to_dict(self) -> dict:
        """Returns a dictionary representation of the object."""

        return {
            "container_name": self.container_name
        }

    @staticmethod
    def to_json(obj: InvoiceBatchRequest) -> str:
        """Converts the object instance to a JSON string. Required for serialization in Azure Functions when passing the result between functions.

        :param obj: The object instance to convert.
        :return: A JSON string representing the object instance.
        """

        return json.dumps(obj.to_dict())

    @staticmethod
    def from_json(json_str: str) -> InvoiceBatchRequest:
        """Converts a JSON string to the object instance. Required for deserialization in Azure Functions when receiving the result from another function.

        :param json_str: The JSON string to convert.
        :return: A object instance created from the JSON string.
        """

        return InvoiceBatchRequest.from_dict(json.loads(json_str))

    @staticmethod
    def from_dict(obj: dict) -> InvoiceBatchRequest:
        """Converts a dictionary to an object instance.

        :param obj: The dictionary to convert.
        :return: A object instance created from the dictionary.
        """

        return InvoiceBatchRequest(
            obj["container_name"]
        )
