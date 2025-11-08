from typing import Any

from cachetools import cached
from cachetools.keys import hashkey
from sqlalchemy import URL
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from aoq_factory.config import get_settings


@cached(cache={})
def get_url(use_async: bool = True) -> URL:
    settings = get_settings()
    return URL.create(
        drivername="postgresql+asyncpg" if use_async else "postgresql+psycopg2",
        database=settings.db_name,
        username=settings.db_username,
        password=settings.db_password,
        host=settings.db_host,
        port=settings.db_port,
    )


@cached(cache={}, key=lambda url, **kwargs: hashkey(url))
def get_async_engine(url: URL, **kwargs) -> AsyncEngine:
    return create_async_engine(url, **kwargs)


@cached(cache={}, key=lambda url, **kwargs: hashkey(url))
def get_async_sessionmaker(
    url: URL, engine_kwargs: dict[str, Any], **kwargs
) -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(bind=get_async_engine(url, **engine_kwargs), **kwargs)
