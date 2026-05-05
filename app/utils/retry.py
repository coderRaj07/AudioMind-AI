from tenacity import retry, stop_after_attempt, wait_exponential


def retry_policy(attempts=3):
    return retry(
        stop=stop_after_attempt(attempts),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True,
    )