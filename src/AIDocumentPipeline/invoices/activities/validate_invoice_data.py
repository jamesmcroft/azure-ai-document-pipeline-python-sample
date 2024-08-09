"""Validates extracted data from an invoice for expected fields.

This module provides the blueprint for an Azure Function activity that validates extracted data from an invoice.
"""

from __future__ import annotations
from enum import Flag, auto
import json
from shared.workflow_result import WorkflowResult
from invoices.invoice_data import InvoiceData
from shared.base_request import BaseRequest
from shared.validation_result import ValidationResult
import azure.durable_functions as df

name = "ValidateInvoiceData"
bp = df.Blueprint()


@bp.function_name(name)
@bp.activity_trigger(input_name="input", activity=name)
def run(input: Request) -> Result:
    """Validates extracted data from an invoice for expected fields.

    :param input: The request containing the extracted invoice data.
    :return: The validation result.
    """

    result = Result(input.name or name)

    validation_result = input.validate()
    if not validation_result.is_valid:
        result.merge(validation_result)
        return result

    data = input.data
    if not data.customer_name:
        result.status |= ResultStatus.CustomerNameMissing
        result.add_error(name, "customer_name is required")

    __validate_products__(data, result)
    __validate_returns__(data, result)

    if result.is_valid:
        result.status = ResultStatus.Success

    return result


def __validate_products__(data: InvoiceData, result: Result):
    if not data.products:
        result.status |= ResultStatus.ProductsMissing
        result.add_error("products is required")
    else:
        total_quantity = sum([p.quantity for p in data.products])
        if total_quantity != data.total_quantity:
            result.status |= ResultStatus.ProductsTotalQuantityInvalid
            result.add_error(
                name, f"products quantity total must match total_quantity. Expected: {data.total_quantity}, Actual: {total_quantity}")

        total_price = sum([p.total for p in data.products])
        if total_price != data.total_price:
            result.status |= ResultStatus.ProductsTotalPriceInvalid
            result.add_error(
                name, f"products price total must match total_price. Expected: {data.total_price}, Actual: {total_price}")

    if not data.products_signatures:
        result.status |= ResultStatus.ProductsDriverSignatureMissing | ResultStatus.ProductsCustomerSignatureMissing
        result.add_error(name, "products_signatures is required")
    else:
        driver_signature = next(
            (s for s in data.products_signatures if s.type == "Driver"), None)
        if not driver_signature:
            result.status |= ResultStatus.ProductsDriverSignatureMissing
            result.add_error(
                name, "products_signatures must contain a driver signature")

        customer_signature = next(
            (s for s in data.products_signatures if s.type == "Customer"), None)
        if not customer_signature:
            result.status |= ResultStatus.ProductsCustomerSignatureMissing
            result.add_error(
                name, "products_signatures must contain a customer signature")


def __validate_returns__(data: InvoiceData, result: Result):
    if not data.returns:
        # Returns are optional
        return

    for i, r in enumerate(data.returns):
        if not r.reason:
            result.status |= ResultStatus.ReturnReasonMissing
            result.add_error(
                name, f"{r.id} must contain a reason for the return")

    if not data.returns_signatures:
        result.status |= ResultStatus.ReturnsDriverSignatureMissing | ResultStatus.ReturnsCustomerSignatureMissing
        result.add_error(name, "returns_signatures is required")
    else:
        driver_signature = next(
            (s for s in data.returns_signatures if s.type == "Driver"), None)
        if not driver_signature:
            result.status |= ResultStatus.ReturnsDriverSignatureMissing
            result.add_error(
                name, "returns_signatures must contain a driver signature")

        customer_signature = next(
            (s for s in data.returns_signatures if s.type == "Customer"), None)
        if not customer_signature:
            result.status |= ResultStatus.ReturnsCustomerSignatureMissing
            result.add_error(
                name, "returns_signatures must contain a customer signature")


class Request(BaseRequest):
    """Defines the request payload for the `ValidateInvoiceData` activity."""

    def __init__(self, name: str, data: InvoiceData):
        """Initializes a new instance of the Request class.

        :param name: The name of the invoice blob.
        :param data: The extracted invoice data.
        """

        super().__init__()
        self.name = name
        self.data = data

    def validate(self) -> ValidationResult:
        result = ValidationResult()

        if not self.name:
            result.add_error("name is required")

        if not self.data:
            result.add_error("data is required")

        return result

    def to_dict(self) -> dict:
        """Returns a dictionary representation of the object."""

        return {
            "name": self.name,
            "data": self.data.to_dict()
        }

    @staticmethod
    def to_json(obj: Request) -> str:
        """Converts the object instance to a JSON string. Required for serialization in Azure Functions when passing the result between functions.

        :param obj: The object instance to convert.
        :return: A JSON string representing the object instance.
        """

        return json.dumps(obj.to_dict())

    @staticmethod
    def from_json(json_str: str) -> Request:
        """Converts a JSON string to the object instance. Required for deserialization in Azure Functions when receiving the result from another function.

        :param json_str: The JSON string to convert.
        :return: A object instance created from the JSON string.
        """

        return Request.from_dict(json.loads(json_str))

    @staticmethod
    def from_dict(obj: dict) -> Request:
        """Converts a dictionary to the object instance.

        :param obj: The dictionary to convert.
        :return: A object instance created from the dictionary.
        """

        return Request(
            obj["name"],
            InvoiceData.from_dict(obj["data"])
        )


class Result(WorkflowResult):
    """Defines the result payload for the `ValidateInvoiceData` activity."""

    def __init__(self, name: str):
        """Initializes a new instance of the Result class.

        :param name: The name of the invoice blob.
        """

        super().__init__(name)
        self.status = ResultStatus.Fail

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "activity_results": [r.to_dict() for r in self.activity_results],
            "is_valid": self.is_valid,
            "messages": self.messages,
            "status": self.status.name
        }

    @staticmethod
    def to_json(obj: Result) -> str:
        """Converts the object instance to a JSON string. Required for serialization in Azure Functions when passing the result between functions.

        :param obj: The object instance to convert.
        :return: A JSON string representing the object instance.
        """

        return json.dumps(obj.to_dict())

    @staticmethod
    def from_json(json_str: str) -> Result:
        """Converts a JSON string to the object instance. Required for deserialization in Azure Functions when receiving the result from another function.

        :param json_str: The JSON string to convert.
        :return: A object instance created from the JSON string.
        """

        return Result.from_dict(json.loads(json_str))

    @staticmethod
    def from_dict(obj: dict) -> Result:
        """Converts a dictionary to the object instance.

        :param obj: The dictionary to convert.
        :return: A object instance created from the dictionary.
        """

        result = Result(obj["name"])
        result.is_valid = obj["is_valid"]
        result.messages = obj["messages"]
        result.activity_results = [WorkflowResult.from_dict(
            r) for r in obj["activity_results"]]

        statuses = obj["status"].split("|")
        for status in statuses:
            result.status |= ResultStatus[status]

        return result


class ResultStatus(Flag):
    """Defines the possible validation statuses for extracted invoice data."""

    Fail = 0
    Success = auto()
    CustomerNameMissing = auto()
    ProductsMissing = auto()
    ProductsTotalQuantityInvalid = auto()
    ProductsTotalPriceInvalid = auto()
    ProductsDriverSignatureMissing = auto()
    ProductsCustomerSignatureMissing = auto()
    ReturnsDriverSignatureMissing = auto()
    ReturnsCustomerSignatureMissing = auto()
    ReturnReasonMissing = auto()
