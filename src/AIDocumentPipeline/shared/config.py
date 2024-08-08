import os

otlp_exporter_endpoint = os.environ.get("OTLP_EXPORTER_ENDPOINT", None)
openai_endpoint = os.environ.get("OPENAI_ENDPOINT", None)
openai_embedding_deployment = os.environ.get(
    "OPENAI_EMBEDDING_DEPLOYMENT", None)
openai_completion_deployment = os.environ.get(
    "OPENAI_COMPLETION_DEPLOYMENT", None)
openai_vision_completion_deployment = os.environ.get(
    "OPENAI_VISION_COMPLETION_DEPLOYMENT", None)
document_intelligence_endpoint = os.environ.get(
    "DOCUMENT_INTELLIGENCE_ENDPOINT", None)
managed_identity_client_id = os.environ.get("MANAGED_IDENTITY_CLIENT_ID", None)
invoices_storage_account_name = os.environ.get(
    "INVOICES_STORAGE_ACCOUNT_NAME", None)
invoices_queue_connection = os.environ.get("INVOICES_QUEUE_CONNECTION", None)