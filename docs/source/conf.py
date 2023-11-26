import os
import sys
from pydantic_settings import BaseSettings
# from src.conf.config import Settings
# Додаємо поточний каталог до шляхів пошуку для модулів
sys.path.insert(0, os.path.abspath('..'))

# Додаємо шлях до кореневого каталогу проекту
sys.path.insert(0, os.path.abspath('C:/Users/offic/MyCode/Python_Web1_1/M14/HW_WEB14'))

# Фіксація параметрів Pydantic для генерації документації Sphinx

POSTGRES_DB="rest_app"
POSTGRES_USER="postgres"
POSTGRES_PASSWORD=567234
POSTGRES_PORT=5432
POSTGRES_HOST="hw_web14-postgres-1"
class Settings(BaseSettings):
    sqlalchemy_database_url: str = "postgresql+psycopg2://${POSTGRES_USER}:${POSTGRES_PASSWORD}@${POSTGRES_HOST}:${POSTGRES_PORT}/${POSTGRES_DB}"
    secret_key: str = "secret_key"
    algorithm: str = "HS256"
    mail_username: str = "olegdenko@meta.ua"
    mail_password: str = "secretPassword357"
    mail_from: str = "olegdenko@meta.ua"
    mail_port: int = 465
    mail_server: str = "smtp.meta.ua"
    redis: str = "redis://hw_web14-redis-1"
    redis_host: str = "hw_web14-redis-1"
    redis_port: int = 6379
    postgres_db: str = "rest_app"
    postgres_user: str = "postgres"
    postgres_password: str = "567234"
    postgres_port: int = 5432
    postgres_host: str = "hw_web14-postgres-1"
    cloudinary_name: str = "dwtilicoq"
    cloudinary_api_key: str = "971622492684357"
    cloudinary_api_secret: str = "-TjMo-OfjFNmLWpZViQkIdZw4_s"

    class Config:
        env_file = "1.env"
        env_file_encoding = "utf-8"

# Підміна налаштувань
settings = Settings()


project = 'Contacts book'
copyright = '2023, OlegDenko'
author = 'OlegDenko'

extensions = ['sphinx.ext.autodoc']

templates_path = ['_templates']
exclude_patterns = ['__build', 'Thumbs.db', '.DS_Store']

html_theme = 'nature'
html_static_path = ['_static']
