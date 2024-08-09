from __future__ import annotations
from invoices import extract_invoice_data_workflow
from shared.workflow_result import WorkflowResult
from invoices.invoice_batch_request import InvoiceBatchRequest
import azure.durable_functions as df
import azure.functions as func
import logging
from invoices.activities import get_invoice_folders

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


@bp.function_name(queue_trigger_name)
@bp.queue_trigger(arg_name="msg", queue_name="invoices", connection="INVOICES_QUEUE_CONNECTION")
@bp.durable_client_input(client_name="client")
async def process_invoice_batch_queue(msg: func.QueueMessage, client: df.DurableOrchestrationClient):
    request_body = msg.get_json()
    invoice_batch_request = InvoiceBatchRequest.from_dict(request_body)

    instance_id = await client.start_new(name, client_input=invoice_batch_request)

    logging.info(f"Started workflow with instance ID: {instance_id}")

    response = client.create_http_management_payload(instance_id)

    logging.info(f"Response: {response}")


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
    extract_invoice_data_tasks = []
    for folder in invoice_folders:
        extract_invoice_data_task = context.call_sub_orchestrator(
            extract_invoice_data_workflow.name, folder)
        extract_invoice_data_tasks.append(extract_invoice_data_task)

    yield context.task_all(extract_invoice_data_tasks)

    for task in extract_invoice_data_tasks:
        logging.info(f"Task {task} completed.")

    return result
