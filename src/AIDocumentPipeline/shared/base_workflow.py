import azure.durable_functions as df


class BaseWorkflow:
    def __init__(self, name: str):
        self.name = name
        self.retry_options = df.RetryOptions(
            max_number_of_attempts=5,
            first_retry_interval_in_milliseconds=5000
        )

    async def start_workflow(self, client: df.DurableOrchestrationClient, input: dict):
        return await client.start_new(self.name, client_input=input)

    async def call_workflow(self, client: df.DurableOrchestrationContext, sub_workflow_name: str, input: dict):
        return await client.call_sub_orchestrator_with_retry(sub_workflow_name, self.retry_options, input_=input)

    async def call_activity(self, client: df.DurableOrchestrationContext, activity_name: str, input: dict):
        return await client.call_activity_with_retry(activity_name, self.retry_options, input_=input)
