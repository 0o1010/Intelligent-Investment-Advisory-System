import os
from typing import List

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DEBUG: bool = True
    PROJECT_NAME: str = "Intelligent Investment Advisory System"
    CONFIG_PATH: str = os.path.dirname(os.path.abspath(__file__))

    # 跨域
    BACKEND_CORS_ORIGINS: List[str] = ['*']




settings = Settings()

