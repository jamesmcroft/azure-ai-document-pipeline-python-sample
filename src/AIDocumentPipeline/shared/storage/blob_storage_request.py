from shared.base_request import BaseRequest


class BlobStorageRequest(BaseRequest):
    def __init__(self, storage_account_name: str, container_name: str, blob_name: str):
        self.storage_account_name = storage_account_name
        self.container_name = container_name
        self.blob_name = blob_name
