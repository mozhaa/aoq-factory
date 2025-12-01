from functools import cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    db_name: str
    db_username: str
    db_password: str
    db_host: str
    db_port: int
    resources_dir: str
    anidb_request_interval: float
    idsmoe_api_key: str
    idsmoe_rate_limiter_max_rate: float
    idsmoe_rate_limiter_time_period: float

    model_config = SettingsConfigDict(env_file=None)


@cache
def get_settings() -> Settings:
    return Settings()  # type: ignore
