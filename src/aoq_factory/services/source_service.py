from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from aoq_factory.api.models.source import CreateSourceRequest, SourceResponse, UpdateSourceRequest
from aoq_factory.database.models import Source
from aoq_factory.deps.engine import EngineDep


class SourceService:
    def __init__(self, engine: EngineDep):
        self.engine = engine

    async def create(self, source: CreateSourceRequest) -> bool:
        async with self.engine.async_session() as session:
            session.add(
                Source(
                    song_id=source.song_id,
                    location=source.location,
                    local_path=source.local_path,
                )
            )
            try:
                await session.commit()
                return True
            except IntegrityError:
                return False

    async def get_all(self) -> list[SourceResponse]:
        async with self.engine.async_session() as session:
            sources = (await session.scalars(select(Source))).all()
            session.expunge_all()
        return [
            SourceResponse(
                id=source.id,
                song_id=source.song_id,
                location=source.location,
                local_path=source.local_path,
                is_downloading=source.is_downloading,
                is_invalid=source.is_invalid,
            )
            for source in sources
        ]

    async def get_one(self, source_id: int) -> SourceResponse | None:
        async with self.engine.async_session() as session:
            source = await session.scalar(select(Source).where(Source.id == source_id))
            if source:
                session.expunge(source)
                return SourceResponse(
                    id=source.id,
                    song_id=source.song_id,
                    location=source.location,
                    local_path=source.local_path,
                    is_downloading=source.is_downloading,
                    is_invalid=source.is_invalid,
                )
            return None

    async def update(self, source_id: int, source: UpdateSourceRequest) -> bool:
        async with self.engine.async_session() as session:
            db_source = await session.scalar(select(Source).where(Source.id == source_id))
            if not db_source:
                return False
            db_source.location = source.location
            db_source.local_path = source.local_path
            db_source.is_downloading = source.is_downloading
            db_source.is_invalid = source.is_invalid
            await session.commit()
            return True

    async def delete(self, source_id: int) -> bool:
        async with self.engine.async_session() as session:
            source = await session.scalar(select(Source).where(Source.id == source_id))
            if not source:
                return False
            await session.delete(source)
            await session.commit()
            return True
