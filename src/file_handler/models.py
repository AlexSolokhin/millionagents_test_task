from typing import Annotated
from uuid import UUID, uuid4

from sqlalchemy.orm import Mapped, mapped_column

from src.config.database import Base


class File(Base):
    __tablename__ = 'files'

    uid: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    file_path: Mapped[str]
    original_name: Mapped[str]
    size: Mapped[int]
    format: Mapped[Annotated[str, 16]]
    extension: Mapped[Annotated[str, 16]]

    def __repr__(self):
        return f'{self.uid} - {self.original_name}.{self.extension}'
