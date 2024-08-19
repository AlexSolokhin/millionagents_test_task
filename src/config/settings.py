import os
from dotenv import load_dotenv

load_dotenv()

# БД
DB_USER = os.getenv('DB_USER', None)
DB_HOST = os.getenv('DB_HOST', None)
DB_PORT = os.getenv('DB_PORT', None)
DB_NAME = os.getenv('DB_NAME', None)
DB_PASSWORD = os.getenv('DB_PASSWORD', None)
DATABASE_URL = f'postgresql+asyncpg://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}'
