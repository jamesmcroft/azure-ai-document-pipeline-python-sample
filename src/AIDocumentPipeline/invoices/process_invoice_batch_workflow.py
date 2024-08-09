"""Processes a batch of invoice folders in a Storage container.

This module defines the workflow to process a batch of invoice folders in a Storage container. The workflow extracts the invoice data from each invoice folder and saves the extracted data to a database.
"""

from __future__ import annotations
from invoices import extract_invoice_data_workflow
from shared.workflow_result import WorkflowResult
from invoices.invoice_batch_request import InvoiceBatchRequest
import azure.durable_functions as df
from azure.durable_functions.models.Task import TaskBase
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
    """Starts a new instance of the ProcessInvoiceBatchWorkflow orchestration in response to an HTTP request.

    :param req: The HTTP request trigger containing the invoice batch request in the body.
    :param client: The Durable Orchestration Client to start the workflow.
    :return: The 202 Accepted response with a dictionary of orchestrator management URLs.
    """

    request_body = req.get_json()
    invoice_batch_request = InvoiceBatchRequest.from_dict(request_body)

    instance_id = await client.start_new(name, client_input=invoice_batch_request)

    logging.info(f"Started workflow with instance ID: {instance_id}")

    return client.create_check_status_response(req, instance_id)


@bp.function_name(queue_trigger_name)
@bp.queue_trigger(arg_name="msg", queue_name="invoices", connection="INVOICES_QUEUE_CONNECTION")
@bp.durable_client_input(client_name="client")
async def process_invoice_batch_queue(msg: func.QueueMessage, client: df.DurableOrchestrationClient):
    """Starts a new instance of the ProcessInvoiceBatchWorkflow orchestration in response to a Storage queue message.

    The dictionary of orchestrator management URLs is logged out for monitoring purposes.

    :param msg: The queue message containing the invoice batch request.
    :param client: The Durable Orchestration Client to start the workflow.
    """

    request_body = msg.get_json()
    invoice_batch_request = InvoiceBatchRequest.from_dict(request_body)

    instance_id = await client.start_new(name, client_input=invoice_batch_request)

    logging.info(f"Started workflow with instance ID: {instance_id}")

    response = client.create_http_management_payload(instance_id)

    logging.info(f"Response: {response}")


@bp.function_name(name)
@bp.orchestration_trigger(context_name="context", orchestration=name)
def run(context: df.DurableOrchestrationContext):
    """Orchestrates the processing of a batch of invoice folders in a Storage container.

    :param context: The Durable Orchestration Context containing the input data for the workflow.
    :return: The `WorkflowResult` of the workflow operation containing the validation messages and activity results.
    """

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
    extract_invoice_data_tasks: list[TaskBase] = []
    for folder in invoice_folders:
        extract_invoice_data_task = context.call_sub_orchestrator(
            extract_invoice_data_workflow.name, folder)
        extract_invoice_data_tasks.append(extract_invoice_data_task)

    yield context.task_all(extract_invoice_data_tasks)

    for task in extract_invoice_data_tasks:
        task_result = WorkflowResult.from_dict(task.result)
        result.add_activity_result(extract_invoice_data_workflow.name,
                                   "Processed invoice folder.",
                                   task_result)

    return result.to_dict()
