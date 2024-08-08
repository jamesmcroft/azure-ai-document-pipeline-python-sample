from __future__ import annotations
import json
from shared.validation_result import ValidationResult
from shared.storage.blob_storage_request import BlobStorageRequest
from shared.storage.azure_storage_client_factory import AzureStorageClientFactory
import shared.identity as identity
import azure.durable_functions as df
import logging

name = "WriteBytesToBlob"
bp = df.Blueprint()
storage_factory = AzureStorageClientFactory(identity.default_credential)


@bp.function_name(name)
@bp.activity_trigger(input_name="input", activity=name)
def run(input: Request) -> bool:
    validation_result = input.validate()
    if not validation_result.is_valid:
        logging.error(f"Invalid input: {validation_result.to_str()}")
        return False

    blob_container_client = storage_factory.get_blob_service_client(
        input.storage_account_name).get_container_client(input.container_name)

    if not blob_container_client.exists():
        blob_container_client.create_container()

    blob_client = blob_container_client.get_blob_client(input.blob_name)

    blob_client.upload_blob(input.content, overwrite=input.overwrite)

    return True


class Request(BlobStorageRequest):
    def __init__(self, storage_account_name: str, container_name: str, blob_name: str, content: bytes, overwrite: bool):
        super().__init__(storage_account_name, container_name, blob_name)
        self.content = content
        self.overwrite = overwrite

    def validate(self) -> ValidationResult:
        result = ValidationResult()

        if not self.storage_account_name:
            result.add_error("storage_account_name is required")

        if not self.container_name:
            result.add_error("container_name is required")

        if not self.blob_name:
            result.add_error("blob_name is required")

        if not self.content:
            result.add_error("content is required")

        return result

    def to_dict(obj: Request) -> dict:
        return {
            "storage_account_name": obj.storage_account_name,
            "container_name": obj.container_name,
            "blob_name": obj.blob_name,
            "content": obj.content.decode("utf-8"),
            "overwrite": obj.overwrite
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
            obj["storage_account_name"],
            obj["container_name"],
            obj["blob_name"],
            str.encode(obj["content"], "utf-8"),
            obj["overwrite"]
        )
