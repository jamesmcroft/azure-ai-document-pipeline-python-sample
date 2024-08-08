import os
from azure.identity import DefaultAzureCredential

managed_identity_client_id = os.environ.get("MANAGED_IDENTITY_CLIENT_ID", None)

default_credential = DefaultAzureCredential(
    exclude_environment_credential=True,
    exclude_interactive_browser_credential=True,
    exclude_visual_studio_code_credential=True,
    exclude_shared_token_cache_credential=True,
    exclude_developer_cli_credential=True,
    exclude_powershell_credential=True,
    exclude_workload_identity_credential=True,
    process_timeout=10,
    managed_identity_client_id=managed_identity_client_id
)
