from functools import cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    db_name: str
    db_username: str
    db_password: str
    db_host: str
    db_port: int

    model_config = SettingsConfigDict(env_file=None)


@cache
def get_settings() -> Settings:
    return Settings()  # type: ignore
