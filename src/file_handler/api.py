import aiofiles
import uuid
from fastapi import FastAPI, File, HTTPException, UploadFile, status
from fastapi.responses import JSONResponse

from .exceptions import CloudError
from .models import File as FileModel
from .services import CloudUploadService, FileService
from ..config.database import session_factory

app = FastAPI(title='File Handler')


@app.post('/upload_file')
async def upload_file(file: UploadFile = File(...)):
    max_file_size = 10
    file_path = await FileService.generate_filepath(file.filename)
    if file.size > 1024 * 1024 * max_file_size:
        return HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Размер файла более {max_file_size} MB. Используйте метод для потоковой загрузки'
        )
    try:
        content = await file.read()
        async with aiofiles.open(file_path, 'wb') as uploaded_file:
            await uploaded_file.write(content)
        await CloudUploadService.upload_file(file_path)
        db_file = FileModel(
            file_path=file_path,
            original_name=file.filename,
            extension=file.filename.split('.')[-1],
            format=file.content_type,
            size=file.size,
        )
        async with session_factory() as session:
            session.add(db_file)
            await session.commit()
    except CloudError as e:
        return HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Не удалось загрузить файл на облако: {type(e)},{e}'
        )
    except Exception as e:
        return HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Ошибка при загрузке файла: {e}'
        )
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={'message': f'Файл {file.filename} успешно загружен'}
    )

@app.post('/upload_stream_file')
async def upload_stream_file(file: UploadFile = File(...)):
    chunk_size = 1024 * 1024 # Можно вынести в переменную окружения или передавать прямо в метод
    file_path = await FileService.generate_filepath(file.filename)
    try:
        async with aiofiles.open(file_path, 'wb') as uploaded_file:
            while content := await file.read(chunk_size):
                await uploaded_file.write(content)
        await CloudUploadService.upload_file(file_path)
        db_file = FileModel(
            file_path=file_path,
            original_name=file.filename,
            extension=file.filename.split('.')[-1],
            format=file.content_type,
            size=file.size,
        )
        async with session_factory() as session:
            session.add(db_file)
            await session.commit()
    except CloudError as e:
        return HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Не удалось загрузить файл на облако: {e}'
        )
    except Exception as e:
        return HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f'Ошибка при загрузке файла: {e}'
        )
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content={'message': f'Файл {file.filename} успешно загружен'}
    )

@app.get('/{uid}', status_code=200)
async def get_file(uid: str):
    async with session_factory() as session:
        file = await session.get(FileModel, uuid.UUID(uid))
    return {
        'uid': file.uid,
        'file_path': file.file_path,
        'original_name': file.original_name,
        'extension': file.extension,
        'format': file.format,
        'size': file.size,
    }
