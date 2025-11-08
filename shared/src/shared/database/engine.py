import asyncio
from typing import Any, Type

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase


class LazyEngine:
    def __init__(
        self,
        url: str,
        base: Type[DeclarativeBase],
        async_session_defaults: dict[str, Any] | None = None,
    ) -> None:
        self.connected = False
        self.url = url
        self.base = base
        if async_session_defaults is not None:
            self.async_session_defaults = async_session_defaults
        else:
            self.async_session_defaults: dict[str, Any] = {}

    def connect(self, echo: bool = False) -> None:
        self._engine = create_async_engine(url=self.url, echo=echo)
        self._async_session = async_sessionmaker(self._engine, class_=AsyncSession)
        self.connected = True

    def async_session(self, **kwargs) -> AsyncSession:
        defaults = self.async_session_defaults.copy()
        defaults.update(kwargs)
        return self._async_session(**defaults)

    async def create_tables(self) -> None:
        async with self._engine.begin() as conn:
            await conn.run_sync(self.base.metadata.create_all)

    async def drop_tables(self) -> None:
        async with self._engine.begin() as conn:
            await conn.run_sync(self.base.metadata.drop_all)

    async def recreate_tables(self) -> None:
        await self.drop_tables()
        await self.create_tables()


engines: dict[str, LazyEngine] = {}
get_engine_lock = asyncio.Lock()


async def get_engine(
    url: str, base: Type[DeclarativeBase], echo: bool = False
) -> LazyEngine:
    async with get_engine_lock:
        global engines
        if url not in engines:
            engine = LazyEngine(url, base)
            engine.connect(echo=echo)
            engines[url] = engine
        return engines[url]
