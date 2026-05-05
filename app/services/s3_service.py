import boto3
from botocore.exceptions import BotoCoreError, ClientError
from app.core.config import get_settings
from app.core.logger import get_logger
from app.utils.retry import retry_policy

settings = get_settings()
logger = get_logger(__name__)

s3_client = boto3.client(
    "s3",
    endpoint_url=settings.S3_ENDPOINT,
    aws_access_key_id=settings.S3_ACCESS_KEY,
    aws_secret_access_key=settings.S3_SECRET_KEY,
)


@retry_policy(3)
def upload_file(file_bytes: bytes, key: str) -> str:
    try:
        s3_client.put_object(
            Bucket=settings.S3_BUCKET,
            Key=key,
            Body=file_bytes,
        )
        return f"{settings.S3_ENDPOINT}/{settings.S3_BUCKET}/{key}"
    except (BotoCoreError, ClientError) as e:
        logger.error(f"S3 upload failed: {e}")
        raise


@retry_policy(3)
def download_file(key: str) -> bytes:
    try:
        response = s3_client.get_object(
            Bucket=settings.S3_BUCKET,
            Key=key,
        )
        return response["Body"].read()
    except (BotoCoreError, ClientError) as e:
        logger.error(f"S3 download failed: {e}")
        raise