from fastapi import UploadFile
import os


def construct_upload_file(path: str, content_type="image/jpeg") -> UploadFile:
    file_size = os.stat(path).st_size
    file = open(path, "rb")
    filename = os.path.basename(path)
    headers = {
        "content-type": content_type,
        "content-length": str(file_size),
    }
    return UploadFile(file=file, filename=filename, size=file_size, headers=headers)
