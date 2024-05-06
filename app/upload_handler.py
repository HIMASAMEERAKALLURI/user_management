from fastapi import UploadFile
from minio import Minio
import json
from app.dependencies import get_settings
from app.utils.generate_upload import construct_upload_file


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

    def bucket_exists(self):
        return self.minio_client.bucket_exists(self.bucket_name)

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
        image = construct_upload_file("assets/image.jpeg")
        self.upload_image("default/avatar.jpeg", image)

    def upload_image(self, object_name: str, image: UploadFile):
        if not image.content_type.startswith("image"):
            raise Exception("Invalid file type")
        return self.upload_file(object_name, image)

    def upload_file(self, object_name: str, file: UploadFile):
        contents = file.file
        content_type = file.content_type
        length = file.size
        self.minio_client.put_object(
            self.bucket_name, object_name, contents, length, content_type
        )
        return f"/{self.bucket_name}/{object_name}"

    def get_presigned_url(self, object_name: str):
        return self.minio_client.presigned_get_object(self.bucket_name, object_name)

    def object_exists(self, object_name: str):
        bucket_name, object_key = object_name.strip("/").split("/", 1)
        return self.minio_client.stat_object(self.bucket_name, object_key)

    @property
    def objects(self):
        return self.minio_client.list_objects(self.bucket_name, recursive=True)

    def delete_bucket(self):
        for object in self.objects:
            self.minio_client.remove_object(self.bucket_name, object.object_name)
        self.minio_client.remove_bucket(self.bucket_name)
