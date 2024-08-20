import aiofiles
from fastapi import FastAPI, File, HTTPException, UploadFile, status
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse

from .exceptions import CloudError
from .services import CloudUploadService, FileService

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
        await FileService.save_file_to_db(
            filename=file.filename,
            path=file_path,
            file_format=file.content_type,
            size=file.size,
        )
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
        await FileService.save_file_to_db(
            filename=file.filename,
            path=file_path,
            file_format=file.content_type,
            size=file.size,
        )
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

@app.get('/{uid}')
async def get_file(uid: str):
    try:
        file_dto = await FileService.get_file_dto(uid)
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content=jsonable_encoder(file_dto)
        )
    except Exception as e:
        return HTTPException(
            status_code=status.HTTP_400_NOT_FOUND,
            detail=f'Ошибка получения файла: {e}'
        )
