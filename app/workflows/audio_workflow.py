from temporalio import workflow
from temporalio.common import RetryPolicy
from datetime import timedelta


@workflow.defn
class AudioIngestionWorkflow:

    @workflow.run
    async def run(self, input_data: dict):
        result = await workflow.execute_activity(
            "process_audio_activity",
            input_data,
            start_to_close_timeout=timedelta(minutes=15),
            retry_policy=RetryPolicy(maximum_attempts=3),
        )
        return result