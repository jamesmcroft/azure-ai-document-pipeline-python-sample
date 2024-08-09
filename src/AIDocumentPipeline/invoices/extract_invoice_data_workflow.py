"""Extract the data from the invoice files in a specific folder of a blob container.

This workflow orchestrates the extraction of data from the invoice files in a specific folder and stores the extracted data back in the blob container.
"""

from __future__ import annotations
from invoices.invoice_data import InvoiceData
from shared.storage import write_bytes_to_blob
from invoices.activities import extract_invoice_data, validate_invoice_data
from shared.workflow_result import WorkflowResult
import azure.durable_functions as df
from shared import config as app_config

name = "ExtractInvoiceDataWorkflow"
bp = df.Blueprint()


@bp.function_name(name)
@bp.orchestration_trigger(context_name="context", orchestration=name)
def run(context: df.DurableOrchestrationContext):
    """Orchestrates the extraction of data from the invoice files in a specific folder and stores the extracted data back in the blob container.

    :param context: The Durable Orchestration Context containing the input data for the workflow.
    :return: The `WorkflowResult` of the workflow operation containing the validation messages and activity results.
    """

    # Step 1: Extract the input from the context
    input = context.get_input()
    result = WorkflowResult(input.name)

    # Step 2: Validate the input
    validation_result = input.validate()
    if not validation_result.is_valid:
        result.merge(validation_result)
        return result

    result.add_message("InvoiceFolder.validate", "input is valid")

    # Step 3: Process each invoice file
    for invoice in input.invoice_file_names:
        invoice_data = yield context.call_activity(extract_invoice_data.name, extract_invoice_data.Request(input.container_name, invoice))

        if not invoice_data:
            result.add_error(extract_invoice_data.name,
                             f"Failed to extract data for {invoice}.")
            continue

        invoice_data_stored = yield context.call_activity(write_bytes_to_blob.name, write_bytes_to_blob.Request(app_config.invoices_storage_account_name, input.container_name, f"{invoice}.Data.json", InvoiceData.to_json(invoice_data).encode("utf-8"), True))

        if not invoice_data_stored:
            result.add_error(write_bytes_to_blob.name,
                             f"Failed to store extracted data for {invoice}.")
            continue

        invoice_data_validation = yield context.call_activity(validate_invoice_data.name, validate_invoice_data.Request(invoice, invoice_data))

        result.merge(invoice_data_validation)

        yield context.call_activity(write_bytes_to_blob.name, write_bytes_to_blob.Request(app_config.invoices_storage_account_name, input.container_name, f"{invoice}.Validation.json", WorkflowResult.to_json(invoice_data_validation).encode("utf-8"), True))

    return result.to_dict()
