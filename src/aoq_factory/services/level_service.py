from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from aoq_factory.api.models.level import CreateLevelRequest, LevelResponse, UpdateLevelRequest
from aoq_factory.database.models import Level
from aoq_factory.deps.engine import EngineDep


class LevelService:
    def __init__(self, engine: EngineDep):
        self.engine = engine

    async def create(self, level: CreateLevelRequest) -> bool:
        async with self.engine.async_session() as session:
            session.add(
                Level(
                    song_id=level.song_id,
                    value=level.value,
                    created_by=level.created_by,
                )
            )
            try:
                await session.commit()
                return True
            except IntegrityError:
                return False

    async def get_all(self) -> list[LevelResponse]:
        async with self.engine.async_session() as session:
            levels = (await session.scalars(select(Level))).all()
            session.expunge_all()
        return [
            LevelResponse(
                id=level.id,
                song_id=level.song_id,
                value=level.value,
                created_by=level.created_by,
            )
            for level in levels
        ]

    async def get_one(self, level_id: int) -> LevelResponse | None:
        async with self.engine.async_session() as session:
            level = await session.scalar(select(Level).where(Level.id == level_id))
            if level:
                session.expunge(level)
                return LevelResponse(
                    id=level.id,
                    song_id=level.song_id,
                    value=level.value,
                    created_by=level.created_by,
                )
            return None

    async def update(self, level_id: int, level: UpdateLevelRequest) -> bool:
        async with self.engine.async_session() as session:
            db_level = await session.scalar(select(Level).where(Level.id == level_id))
            if not db_level:
                return False
            db_level.value = level.value
            db_level.created_by = level.created_by
            await session.commit()
            return True

    async def delete(self, level_id: int) -> bool:
        async with self.engine.async_session() as session:
            level = await session.scalar(select(Level).where(Level.id == level_id))
            if not level:
                return False
            await session.delete(level)
            await session.commit()
            return True
