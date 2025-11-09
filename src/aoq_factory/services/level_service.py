from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from aoq_factory.api.models.level import CreateLevelRequest, LevelResponse, UpdateLevelRequest
from aoq_factory.database.models import Level
from aoq_factory.deps.engine import EngineDep

from .exc import InvalidLevelValue, NoSuchLevel, NoSuchSong


class LevelService:
    def __init__(self, engine: EngineDep):
        self.engine = engine

    async def create(self, level: CreateLevelRequest) -> None:
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
            except IntegrityError as e:
                error_str = str(e.orig).lower()
                if "fk_levels_song_id_songs" in error_str:
                    raise NoSuchSong() from e
                elif "ck_levels_value_range" in error_str:
                    raise InvalidLevelValue() from e
                raise

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

    async def get_one(self, level_id: int) -> LevelResponse:
        async with self.engine.async_session() as session:
            level = await session.scalar(select(Level).where(Level.id == level_id))
            if level is None:
                raise NoSuchLevel()
            session.expunge(level)
        return LevelResponse(
            id=level.id,
            song_id=level.song_id,
            value=level.value,
            created_by=level.created_by,
        )

    async def update(self, level_id: int, level: UpdateLevelRequest) -> None:
        async with self.engine.async_session() as session:
            db_level = await session.scalar(select(Level).where(Level.id == level_id))
            if db_level is None:
                raise NoSuchLevel()
            db_level.value = level.value
            db_level.created_by = level.created_by
            await session.commit()

    async def delete(self, level_id: int) -> None:
        async with self.engine.async_session() as session:
            level = await session.scalar(select(Level).where(Level.id == level_id))
            if level is None:
                raise NoSuchLevel()
            await session.delete(level)
            await session.commit()
