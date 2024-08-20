from fastapi import FastAPI

from .file_handler.api import files

app = FastAPI(
    title='File Handler',
    openapi_url="/api/v1/files/openapi.json",
    docs_url="/api/v1/files/docs"
)

app.include_router(files, prefix='/api/v1/files', tags=['Управление файлами'])