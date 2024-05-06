import pytest
import io
from app.upload_handler import MinioClient
from app.utils.generate_upload import construct_upload_file
from fastapi import UploadFile
import os


@pytest.fixture(scope="module")
def minio_client():
    return MinioClient("test-bucket")


def test_bucket_exists(minio_client):
    # Call the function
    result = minio_client.bucket_exists()

    # Check the result
    assert result is True


def test_upload_image_valid(minio_client):
    # Prepare test data
    object_name = "test_image.jpg"
    image = construct_upload_file("assets/image.jpeg")

    # Call the function
    result = minio_client.upload_image(object_name, image)

    # Check the result
    assert result == f"/test-bucket/{object_name}"
    objects = minio_client.objects
    assert any(obj.object_name == object_name for obj in objects)


def test_upload_image_invalid_type(minio_client):
    # Prepare test data
    object_name = "test_image.txt"
    image = construct_upload_file("assets/text.txt", content_type="text/plain")

    # Call the function and expect an exception
    with pytest.raises(Exception) as exc_info:
        minio_client.upload_image(object_name, image)
    assert str(exc_info.value) == "Invalid file type"


def test_get_presigned_url(minio_client):
    # Prepare test data
    object_name = "test_image.jpg"
    image = construct_upload_file("assets/image.jpeg")

    minio_client.upload_file(object_name, image)

    # Call the function
    result = minio_client.get_presigned_url(object_name)

    # Check the result
    assert "test-bucket/test_image.jpg" in result
    assert "X-Amz-Algorithm" in result


def test_delete_bucket(minio_client):
    # Call the function
    minio_client.delete_bucket()

    # Check if the bucket is deleted
    assert not minio_client.bucket_exists()
