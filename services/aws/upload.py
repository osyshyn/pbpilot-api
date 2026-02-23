from io import BytesIO

from fastapi import UploadFile

from exceptions import EmptyFileException, EmptyFileNameException
from services.aws import S3Actions


class FileUploadService:
    _EMPTY_FILE_SIZE: int = 0
    def __init__(self, s3_actions: S3Actions) -> None:
        self._s3 = s3_actions

    async def upload_files(
        self,
        files: list[UploadFile],
        prefix: str,
    ) -> list[tuple[str, str]]:
        results = []
        for file in files:
            if not file.filename:
                raise EmptyFileNameException
            content = await file.read()
            if len(content) == FileUploadService._EMPTY_FILE_SIZE:
                raise EmptyFileException

            key, content_type = self._s3.upload_file(
                file_obj=BytesIO(content),
                file_name=file.filename,
                file_size=len(content),
                declared_content_type=file.content_type,
                prefix=prefix,
            )
            results.append((key, content_type))
        return results