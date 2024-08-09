"""Write bytes to a blob in Azure Blob Storage.

This module provides the blueprint for an Azure Function activity that writes a byte array to a blob in Azure Blob Storage.
"""

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
    """Writes a byte array to a blob in Azure Blob Storage.

    :param input: The blob storage information including the buffer byte array, storage account, container, and blob name.
    :return: True if the byte array was successfully written to the blob; otherwise, False.
    """

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
    """Defines the request payload for the `WriteBytesToBlob` activity."""

    def __init__(self, storage_account_name: str, container_name: str, blob_name: str, content: bytes, overwrite: bool = True):
        """Initializes a new instance of the Request class.

        :param storage_account_name: The name of the Azure Storage account.
        :param container_name: The name of the container within the storage account to write the content to.
        :param blob_name: The name of the blob to write the content to.
        :param content: The byte array content to write to the blob.
        :param overwrite: A flag indicating whether to overwrite an existing blob with the same name. Default is `True`.
        """

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

    def to_dict(self) -> dict:
        """Returns a dictionary representation of the object."""

        return {
            "storage_account_name": self.storage_account_name,
            "container_name": self.container_name,
            "blob_name": self.blob_name,
            "content": self.content.decode("utf-8"),
            "overwrite": self.overwrite
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
        """Converts a dictionary to an object instance.

        :param obj: The dictionary to convert.
        :return: A object instance created from the dictionary.
        """

        return Request(
            obj["storage_account_name"],
            obj["container_name"],
            obj["blob_name"],
            str.encode(obj["content"], "utf-8"),
            obj["overwrite"]
        )
