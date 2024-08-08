from __future__ import annotations
from shared.workflow_result import WorkflowResult
from invoices.invoice_batch_request import InvoiceBatchRequest
from shared import config as app_config
import azure.durable_functions as df
import azure.functions as func
import logging
from invoices.activities import extract_invoice_data, get_invoice_folders

name = "ProcessInvoiceBatchWorkflow"
http_trigger_name = "ProcessInvoiceBatchHttp"
queue_trigger_name = "ProcessInvoiceBatchQueue"
bp = df.Blueprint()


@bp.function_name(http_trigger_name)
@bp.route(route="invoices", methods=["POST"])
@bp.durable_client_input(client_name="client")
async def process_invoice_batch_http(req: func.HttpRequest, client: df.DurableOrchestrationClient):
    request_body = req.get_json()
    invoice_batch_request = InvoiceBatchRequest.from_dict(request_body)

    instance_id = await client.start_new(name, client_input=invoice_batch_request)

    logging.info(f"Started workflow with instance ID: {instance_id}")

    return client.create_check_status_response(req, instance_id)


@bp.function_name(name)
@bp.orchestration_trigger(context_name="context", orchestration=name)
def run(context: df.DurableOrchestrationContext) -> WorkflowResult:
    # Step 1: Extract the input from the context
    input = context.get_input()
    result = WorkflowResult(name)

    # Step 2: Validate the input
    validation_result = input.validate()
    if not validation_result.is_valid:
        result.merge(validation_result)
        return result

    result.add_message("InvoiceBatchRequest.validate", "input is valid")

    # Step 3: Get the invoice folders from the blob container
    invoice_folders = yield context.call_activity(get_invoice_folders.name, input)

    result.add_message(get_invoice_folders.name,
                       f"Retrieved {len(invoice_folders)} invoice folders.")

    # Step 4: Process the invoices in each folder.

    return result
