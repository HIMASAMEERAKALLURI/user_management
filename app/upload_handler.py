from fastapi import UploadFile
from minio import Minio
import json
from app.dependencies import get_settings

settings = get_settings()


minio_client = Minio(
    settings.minio_endpoint,
    access_key=settings.minio_access_key,
    secret_key=settings.minio_secret_key,
    secure=settings.minio_secure,
)

bucket_name = "uploads"

bucket_policy = {
    "Version": "2012-10-17",
    "Statement": [
        {
            "Action": ["s3:GetObject"],
            "Effect": "Allow",
            "Principal": {"AWS": ["*"]},
            "Resource": [f"arn:aws:s3:::{bucket_name}/*"],
            "Sid": "",
        }
    ],
}


def initialize_bucket():
    try:
        minio_client.make_bucket(bucket_name)
    except Exception:
        pass
    try:
        minio_client.set_bucket_policy(bucket_name, json.dumps(bucket_policy))
    except Exception:
        pass


def upload_profile_picture(username: str, file: UploadFile):
    filename = file.filename
    object_name = f"{username}/{filename}"
    contents = file.file
    content_type = file.content_type
    length = file.size
    if not content_type.startswith("image"):
        raise Exception("Invalid file type")
    minio_client.put_object(bucket_name, object_name, contents, length, content_type)
    return f"/{bucket_name}/{object_name}"


def get_presigned_url(object_name: str):
    return minio_client.presigned_get_object(bucket_name, object_name)
