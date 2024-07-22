from typing import Optional

from pydantic import AnyHttpUrl
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    pdfact_url: Optional[AnyHttpUrl] = None

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()
