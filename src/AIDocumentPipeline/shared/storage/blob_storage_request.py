from shared.base_request import BaseRequest


class BlobStorageRequest(BaseRequest):
    """Defines the base class for requests to interact with Azure Blob Storage."""

    def __init__(self, storage_account_name: str, container_name: str, blob_name: str):
        """Initializes a new instance of the BlobStorageRequest class.

        :param storage_account_name: The name of the Azure Storage account.
        :param container_name: The name of the container within the storage account.
        :param blob_name: The name of the blob within the container.
        """

        self.storage_account_name = storage_account_name
        self.container_name = container_name
        self.blob_name = blob_name
