from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict

from app.core.paths import ensure_data_dir


class Settings(BaseSettings):
    vk_token: str = ''
    vk_api_version: str = '5.199'
    comments_per_post_limit: int = 300
    default_max_posts: int = 1200
    default_load_comments: bool = True

    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        extra='ignore',
    )

    @property
    def db_path(self) -> Path:
        return ensure_data_dir()


settings = Settings()
