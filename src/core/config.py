import os
from logging import config as logging_config

from pydantic import BaseSettings
from pydantic.fields import Field
from pydantic.networks import PostgresDsn

from src.core.logger import LOGGING

logging_config.dictConfig(LOGGING)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


class AppSettings(BaseSettings):

    app_title: str = 'File storage service'
    tag_auth = 'Registration and authentication'
    database_dsn: PostgresDsn = Field(
        'postgresql+asyncpg://postgres:postgres@localhost:5432/postgres',
        env='DATABASE_DSN'
    )
    project_host: str = Field('127.0.0.1', env='PROJECT_HOST')
    project_port: int = Field(8000, env='PROJECT_PORT')
    engine_echo: bool = Field(False, env='ENGINE_ECHO')
    file_folder: str = Field('files', env='FILE_FOLDER')
    max_file_size: int = Field(1024 * 1024, env='MAX_FILE_SIZE')
    jwt_secret: str = Field('SECRET', env='JWT_SECRET')
    token_lifetime: int = Field(3600, env='TOKEN_LIFETIME')

    class Config:
        env_file = '.env'


app_settings = AppSettings()
