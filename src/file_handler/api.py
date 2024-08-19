from fastapi import FastAPI, File, UploadFile

from .models import File

app = FastAPI(title='File Handler')


@app.post('/upload_file', status_code=201)
async def upload_file(file: UploadFile = File(...)):

    return {'message': f'Файл {file.filename} успешно загружен'}

@app.post('/upload_stream_file', status_code=201)
async def upload_stream_file(file: UploadFile = File(...)):

    return {'message': f'Файл {file.filename} успешно загружен'}

@app.get('/{uid}', status_code=200)
async def get_file(uid: str):

    return {'file': {}}
