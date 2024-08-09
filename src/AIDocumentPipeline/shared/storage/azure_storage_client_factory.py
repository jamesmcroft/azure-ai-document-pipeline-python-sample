import re
from azure.identity import DefaultAzureCredential
from azure.storage.blob import BlobServiceClient


class AzureStorageClientFactory:
    """Defines a factory class for creating Azure Storage service client instances."""

    def __init__(self, credential: DefaultAzureCredential):
        """Initializes a new instance of the AzureStorageClientFactory class.

        :param credential: The Azure credential to use for authenticating with the Azure Storage service.
        """

        self.credential = credential

    def get_blob_service_client(self, storage_account_name: str) -> BlobServiceClient:
        """Retrieves a `BlobServiceClient` instance for the specified Azure Storage account.

        :param storage_account_name: The name of the Azure Storage account. If the account is a development storage account (i.e., devstoreaccount1 or UseDevelopmentStorage=true), the client will be created using the development storage connection string.
        :return: A `BlobServiceClient` instance for the specified storage account.
        """

        if self.__is_development_storage_account__(storage_account_name):
            return BlobServiceClient.from_connection_string("AccountName=devstoreaccount1;AccountKey=Eby8vdM02xNOcqFlqUwJPLlmEtlCDXJ1OUzFT50uSRZ6IFsuFq2UVErCz4I6tq/K1SZFPTOtr/KBHBeksoGMGw==;DefaultEndpointsProtocol=http;BlobEndpoint=http://127.0.0.1:10000/devstoreaccount1;QueueEndpoint=http://127.0.0.1:10001/devstoreaccount1;TableEndpoint=http://127.0.0.1:10002/devstoreaccount1;")
        else:
            return BlobServiceClient(
                f"https://{storage_account_name}.blob.core.windows.net",
                credential=self.credential
            )

    def get_blob_content(self, storage_account_name: str, container_name: str, blob_name: str) -> bytes:
        """Retrieves the content of a specific blob in Azure Blob Storage as a byte array.

        :param storage_account_name: The name of the Azure Storage account.
        :param container_name: The name of the container within the storage account.
        :param blob_name: The name of the blob to retrieve.
        :return: The byte array content of the specified blob.
        """

        blob_service_client = self.get_blob_service_client(
            storage_account_name)
        blob_client = blob_service_client.get_blob_client(
            container_name, blob_name)
        return blob_client.download_blob().readall()

    def get_blobs_by_folder_at_root(self, storage_account_name: str, container_name: str, regex_filter: str | None = None) -> dict[str, list[str]]:
        """Retrieves a list of blob names grouped by folder at the root level of the container.

        Any blobs in the root of the container are grouped by the folder name.

        :param storage_account_name: The name of the Azure Storage account.
        :param container_name: The name of the container within the storage account.
        :param regex_filter: An optional regular expression filter to apply to the blob names.
        :return: A dictionary containing the blob names grouped by folder.
        """

        blob_service_client = self.get_blob_service_client(
            storage_account_name)
        container_client = blob_service_client.get_container_client(
            container_name)

        blob_names = []

        for blob in container_client.list_blobs():
            if not regex_filter or re.match(regex_filter, blob.name):
                blob_names.append(blob.name)

        # If there are blob names that don't contain a '/', append the container name to the start of the blob name
        # Otherwise, return the blob names as is
        blob_names = list(
            map(lambda x: f"{container_name}/{x}" if x.find('/') == -1 else x, blob_names))

        grouped_folders = {}
        for blob_name in blob_names:
            folder_name = blob_name.split('/')[0]
            if folder_name not in grouped_folders:
                grouped_folders[folder_name] = []
            grouped_folders[folder_name].append(blob_name)

        return grouped_folders

    def __is_development_storage_account__(self, storage_account_name: str) -> bool:
        return storage_account_name and (storage_account_name.lower() == "devstoreaccount1" or storage_account_name.lower().startswith("usedevelopmentstorage"))
