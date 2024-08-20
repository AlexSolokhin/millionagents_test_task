import aiohttp
import aiofiles
import os
import uuid

from .dto import FileDTO
from .models import File
from .exceptions import CloudAuthError, CloudError, CloudFileUploadError
from ..config.database import session_factory
from ..config.settings import BASE_DIR


class FileService:
    @classmethod
    async def generate_filepath(cls, filename: str) -> str:
        file_dir = await cls._get_or_create_file_dir()
        return os.path.join(file_dir, filename)

    @classmethod
    async def save_file_to_db(cls, filename: str, path: str, file_format: str, size: int) -> None:
        db_file = File(
            original_name=filename,
            file_path=path,
            extension=filename.split('.')[-1],
            format=file_format,
            size=size,
        )
        async with session_factory() as session:
            session.add(db_file)
            await session.commit()

    @classmethod
    async def get_file_dto(cls, uid: str) -> FileDTO:
        async with session_factory() as session:
            file = await session.get(File, uuid.UUID(uid))
        return FileDTO.model_validate(file, from_attributes=True)


    @classmethod
    async def _get_or_create_file_dir(cls) -> str:
        file_dir = os.path.join(BASE_DIR, 'files')
        if not os.path.exists(file_dir):
            os.makedirs(file_dir)
        return file_dir


class CloudUploadService:
    base_url = os.getenv('CLOUD_URL')
    base_auth = aiohttp.BasicAuth(os.getenv('CLOUD_LOGIN'), os.getenv('CLOUD_PASSWORD'))

    @classmethod
    async def upload_file(cls, file_path: str) -> None:
        url = await cls._get_url()
        file = await cls._get_file(file_path)

        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url=url, data=file, timeout=5) as response:
                    await cls._validate_response(response)
        except (aiohttp.ClientConnectorError, CloudFileUploadError):
            # Т.к. мы стучимся на несуществующий эндпойнт, ловим CloudFileUploadError, которая неизбежно произойдёт
            # Апи условно, поэтому просто выходим из метода после того, как поймали ошибку
            return


    @classmethod
    async def _get_url(cls) -> str:
        return cls.base_url + '/upload_file/'

    @classmethod
    async def _get_file(cls, file_path: str) -> dict:
        return {'file': aiofiles.open(file_path, mode='rb')}

    @staticmethod
    async def _validate_response(response: aiohttp.ClientResponse) -> None:
        if response.status >= 500:
            raise CloudError(f'{response.status} - {response.text}')
        if response.status in (401, 403):
            raise CloudAuthError(f'{response.status} - {response.text}')
        if response.status >= 400:
            raise CloudFileUploadError(f'{response.status} - {response.text}')
