import azure.functions as func
import azure.durable_functions as df
from invoices import process_invoice_batch_workflow
from invoices.activities import extract_invoice_data, get_invoice_folders
from shared.storage import write_bytes_to_blob

app = df.DFApp(http_auth_level=func.AuthLevel.ANONYMOUS)
app.register_functions(write_bytes_to_blob.bp)
app.register_functions(extract_invoice_data.bp)
app.register_functions(get_invoice_folders.bp)
app.register_functions(process_invoice_batch_workflow.bp)
