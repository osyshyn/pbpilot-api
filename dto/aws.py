from dataclasses import dataclass

from core.dto import BaseDTO


@dataclass(slots=True)
class UploadFileDTO(BaseDTO):
    key: str
    file_type: str
