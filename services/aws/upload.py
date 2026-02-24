from io import BytesIO

from fastapi import UploadFile

from dto import UploadFileDTO
from exceptions import EmptyFileException, EmptyFileNameException
from services.aws import S3Actions


class FileUploadService:
    _EMPTY_FILE_SIZE: int = 0

    def __init__(self) -> None:
        self._s3: S3Actions = S3Actions()

    async def upload_files(
        self,
        files: list[UploadFile] | UploadFile,
        prefix: str,
    ) -> list[UploadFileDTO]:
        normalized_files: list[UploadFile] = (
            files if isinstance(files, list) else [files]
        )
        results: list[UploadFileDTO] = []
        for file in normalized_files:
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
            results.append(
                UploadFileDTO(
                    key=key,
                    file_type=content_type,
                )
            )
        return results
