from fastapi import UploadFile
from minio import Minio
import json
from app.dependencies import get_settings


class MinioClient:
    def __init__(self, bucket_name):
        self.settings = get_settings()
        self.bucket_name = bucket_name
        self.minio_client = Minio(
            self.settings.minio_endpoint,
            access_key=self.settings.minio_access_key,
            secret_key=self.settings.minio_secret_key,
            secure=self.settings.minio_secure,
        )
        self.bucket_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Action": ["s3:GetObject"],
                    "Effect": "Allow",
                    "Principal": {"AWS": ["*"]},
                    "Resource": [f"arn:aws:s3:::{self.bucket_name}/*"],
                    "Sid": "",
                }
            ],
        }
        self.initialize_bucket()

    def initialize_bucket(self):
        try:
            self.minio_client.make_bucket(self.bucket_name)
        except Exception:
            pass
        try:
            self.minio_client.set_bucket_policy(
                self.bucket_name, json.dumps(self.bucket_policy)
            )
        except Exception:
            pass

    def upload_profile_picture(self, username: str, file: UploadFile):
        filename = file.filename
        object_name = f"{username}/{filename}"
        contents = file.file
        content_type = file.content_type
        length = file.size
        if not content_type.startswith("image"):
            raise Exception("Invalid file type")
        self.minio_client.put_object(
            self.bucket_name, object_name, contents, length, content_type
        )
        return f"/{self.bucket_name}/{object_name}"

    def get_presigned_url(self, object_name: str):
        return self.minio_client.presigned_get_object(self.bucket_name, object_name)
