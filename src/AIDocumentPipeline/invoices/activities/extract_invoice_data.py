from __future__ import annotations
import json
from shared.documents.document_data_extractor import DocumentDataExtractor, DocumentDataExtractorOptions
from invoices.invoice_data import InvoiceData
from shared.base_request import BaseRequest
from shared.validation_result import ValidationResult
from shared.storage.azure_storage_client_factory import AzureStorageClientFactory
import shared.identity as identity
from shared import config as app_config
import azure.durable_functions as df
import logging

name = "ExtractInvoiceData"
bp = df.Blueprint()
storage_factory = AzureStorageClientFactory(identity.default_credential)
document_extractor = DocumentDataExtractor(identity.default_credential)


@bp.function_name(name)
@bp.activity_trigger(input_name="input", activity=name)
def run(input: Request) -> InvoiceData | None:
    validation_result = input.validate()
    if not validation_result.is_valid:
        logging.error(f"Invalid input: {validation_result.to_str()}")
        return None

    blob_content = storage_factory.get_blob_content(
        app_config.invoices_storage_account_name, input.container_name, input.blob_name)

    data = document_extractor.from_bytes(
        blob_content, DocumentDataExtractorOptions(
            system_prompt="You are an AI assistant that extracts data from documents and returns them as structured JSON objects. Do not return as a code block.",
            extraction_prompt=f"Extract the data from this invoice. If a value is not present, provide null. Use the following structure: {InvoiceData.empty().to_dict()}",
            endpoint=app_config.openai_endpoint,
            deployment_name=app_config.openai_completion_deployment,
            max_tokens=4096,
            temperature=0.1,
            top_p=0.1
        ))

    return InvoiceData.from_dict(data)


class Request(BaseRequest):
    def __init__(self, container_name: str, blob_name: str):
        super().__init__()
        self.container_name = container_name
        self.blob_name = blob_name

    def validate(self) -> ValidationResult:
        result = ValidationResult()

        if not self.container_name:
            result.add_error("container_name is required")

        if not self.blob_name:
            result.add_error("blob_name is required")

        return result

    def to_dict(obj: Request) -> dict:
        return {
            "container_name": obj.container_name,
            "blob_name": obj.blob_name
        }

    @staticmethod
    def to_json(obj: Request) -> str:
        return json.dumps(obj.to_dict())

    @staticmethod
    def from_json(json_str: str) -> Request:
        return Request.from_dict(json.loads(json_str))

    @staticmethod
    def from_dict(obj: dict) -> Request:
        return Request(
            obj["container_name"],
            obj["blob_name"]
        )
