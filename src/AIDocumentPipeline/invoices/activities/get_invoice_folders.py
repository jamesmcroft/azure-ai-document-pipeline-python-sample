"""Get the invoice folders from a blob container.

This module provides the blueprint for an Azure Function activity that retrieves the invoice folders from a container in Azure Blob Storage.
"""

from __future__ import annotations
from invoices.invoice_batch_request import InvoiceBatchRequest
from invoices.invoice_folder import InvoiceFolder
from shared.storage.azure_storage_client_factory import AzureStorageClientFactory
import shared.identity as identity
from shared import config as app_config
import azure.durable_functions as df
import logging

name = "GetInvoiceFolders"
bp = df.Blueprint()
storage_factory = AzureStorageClientFactory(identity.default_credential)


@bp.function_name(name)
@bp.activity_trigger(input_name="input", activity=name)
def run(input: InvoiceBatchRequest) -> list[InvoiceFolder]:
    """Retrieves the invoice folders from a container in Azure Blob Storage.

    :param input: The invoice batch request containing the container name.
    :return: A list of `InvoiceFolder` objects representing the invoice folders in the container.
    """

    grouped_invoices = storage_factory.get_blobs_by_folder_at_root(
        app_config.invoices_storage_account_name, input.container_name, ".*\\.(pdf)$")

    logging.info(
        f"Found {len(grouped_invoices)} folders in {input.container_name}")

    result = []
    for folder_name, invoice_file_names in grouped_invoices.items():
        result.append(InvoiceFolder(input.container_name,
                      folder_name, invoice_file_names))

    return result
