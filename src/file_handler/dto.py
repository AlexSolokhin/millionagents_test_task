from uuid import UUID
from pydantic import BaseModel


class FileDTO(BaseModel):
    uid: UUID
    file_path: str
    original_name: str
    size: int
    format: str
    extension: str