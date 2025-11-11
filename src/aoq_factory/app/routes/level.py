from typing import Optional

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from aoq_factory.app.deps.engine import EngineDep
from aoq_factory.database.models import Level

router = APIRouter(prefix="/levels")


class CreateLevelRequest(BaseModel):
    song_id: int
    value: int
    added_by: str


class LevelResponse(BaseModel):
    id: int
    song_id: int
    value: int
    added_by: str


class UpdateLevelRequest(BaseModel):
    value: Optional[int] = None
    added_by: Optional[str] = None


@router.get("", tags=["level"])
async def get_all(engine: EngineDep) -> list[LevelResponse]:
    async with engine.async_session() as session:
        levels: list[Level] = (await session.scalars(select(Level))).all()
        session.expunge_all()
    return [
        LevelResponse(
            id=level.id,
            song_id=level.song_id,
            value=level.value,
            added_by=level.added_by,
        )
        for level in levels
    ]


@router.get("/{level_id}", tags=["level"])
async def get(engine: EngineDep, level_id: int) -> LevelResponse:
    async with engine.async_session() as session:
        level: Level = await session.scalar(select(Level).where(Level.id == level_id))
        if level is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Level not found")
        session.expunge(level)
    return LevelResponse(
        id=level.id,
        song_id=level.song_id,
        value=level.value,
        added_by=level.added_by,
    )


@router.post("", tags=["level"], status_code=status.HTTP_201_CREATED)
async def create(engine: EngineDep, level: CreateLevelRequest) -> None:
    async with engine.async_session() as session:
        session.add(
            Level(
                song_id=level.song_id,
                value=level.value,
                added_by=level.added_by,
            )
        )
        try:
            await session.commit()
        except IntegrityError as e:
            error_str = str(e.orig).lower()
            if "fk_levels_song_id_songs" in error_str:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Song not found") from e
            elif "ck_levels_value_range" in error_str:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, detail="Level value must be between 0 and 100"
                ) from e
            raise


@router.put("/{level_id}", tags=["level"])
async def update(engine: EngineDep, level_id: int, level: UpdateLevelRequest) -> None:
    async with engine.async_session() as session:
        db_level: Level = await session.scalar(select(Level).where(Level.id == level_id))
        if db_level is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Level not found")

        if level.value is not None:
            db_level.value = level.value
        if level.added_by is not None:
            db_level.added_by = level.added_by

        await session.commit()


@router.delete("/{level_id}", tags=["level"])
async def delete(engine: EngineDep, level_id: int) -> None:
    async with engine.async_session() as session:
        level: Level = await session.scalar(select(Level).where(Level.id == level_id))
        if level is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Level not found")
        await session.delete(level)
        await session.commit()
