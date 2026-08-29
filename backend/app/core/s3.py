import boto3
from botocore.exceptions import ClientError

from app.core.config import settings

_s3_client = None

def get_s3_client():
    global _s3_client
    if _s3_client is None:
        if not all([settings.s3_endpoint, settings.s3_access_key, settings.s3_secret_key]):
            return None
        _s3_client = boto3.client(
            "s3",
            endpoint_url=settings.s3_endpoint,
            aws_access_key_id=settings.s3_access_key,
            aws_secret_access_key=settings.s3_secret_key,
        )
    return _s3_client

def upload_file(file_obj, key: str, content_type: str | None = None) -> str:
    """Upload file to S3, return object key"""
    client = get_s3_client()
    if not client:
        raise RuntimeError("S3 not configured")

    extra_args = {}
    if content_type:
        extra_args["ContentType"] = content_type

    client.upload_fileobj(file_obj, settings.s3_bucket, key, ExtraArgs=extra_args)
    return key

def generate_presigned_url(key: str, expiration: int = 3600) -> str:
    """Generate presigned URL for download"""
    client = get_s3_client()
    if not client:
        raise RuntimeError("S3 not configured")

    return client.generate_presigned_url(
        "get_object",
        Params={"Bucket": settings.s3_bucket, "Key": key},
        ExpiresIn=expiration,
    )

def delete_file(key: str) -> bool:
    """Delete file from S3"""
    client = get_s3_client()
    if not client:
        raise RuntimeError("S3 not configured")

    try:
        client.delete_object(Bucket=settings.s3_bucket, Key=key)
        return True
    except ClientError:
        return False

def file_exists(key: str) -> bool:
    """Check if file exists in S3"""
    client = get_s3_client()
    if not client:
        return False

    try:
        client.head_object(Bucket=settings.s3_bucket, Key=key)
        return True
    except ClientError:
        return False
