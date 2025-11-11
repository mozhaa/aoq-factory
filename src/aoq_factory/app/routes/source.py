from typing import Any, Optional

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from aoq_factory.app.deps.engine import EngineDep
from aoq_factory.database.models import Source, SourceStatus

router = APIRouter(prefix="/sources")


class CreateSourceRequest(BaseModel):
    song_id: int
    location: dict[str, Any]
    local_path: Optional[str]
    added_by: str
    status: Optional[str] = None


class SourceResponse(BaseModel):
    id: int
    song_id: int
    location: dict[str, Any]
    local_path: Optional[str]
    added_by: str
    status: str


class UpdateSourceRequest(BaseModel):
    location: Optional[dict[str, Any]] = None
    local_path: Optional[str] = None
    added_by: Optional[str] = None
    status: Optional[str] = None


@router.get("", tags=["source"])
async def get_all(engine: EngineDep) -> list[SourceResponse]:
    async with engine.async_session() as session:
        sources: list[Source] = (await session.scalars(select(Source))).all()
        session.expunge_all()
    return [
        SourceResponse(
            id=source.id,
            song_id=source.song_id,
            location=source.location,
            local_path=source.local_path,
            added_by=source.added_by,
            status=source.status.name,
        )
        for source in sources
    ]


@router.get("/{source_id}", tags=["source"])
async def get(engine: EngineDep, source_id: int) -> SourceResponse:
    async with engine.async_session() as session:
        source: Source = await session.scalar(select(Source).where(Source.id == source_id))
        if source is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Source not found")
        session.expunge(source)
    return SourceResponse(
        id=source.id,
        song_id=source.song_id,
        location=source.location,
        local_path=source.local_path,
        added_by=source.added_by,
        status=source.status.name,
    )


@router.post("", tags=["source"], status_code=status.HTTP_201_CREATED)
async def create(engine: EngineDep, source: CreateSourceRequest) -> None:
    async with engine.async_session() as session:
        status_enum = SourceStatus.NORMAL
        if source.status is not None:
            if source.status not in SourceStatus.__members__:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid status")
            status_enum = SourceStatus[source.status]

        session.add(
            Source(
                song_id=source.song_id,
                location=source.location,
                local_path=source.local_path,
                added_by=source.added_by,
                status=status_enum,
            )
        )
        try:
            await session.commit()
        except IntegrityError as e:
            error_str = str(e.orig).lower()
            if "fk_sources_song_id_songs" in error_str:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Song not found") from e
            raise


@router.put("/{source_id}", tags=["source"])
async def update(engine: EngineDep, source_id: int, source: UpdateSourceRequest) -> None:
    async with engine.async_session() as session:
        db_source: Source = await session.scalar(select(Source).where(Source.id == source_id))
        if db_source is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Source not found")

        if source.location is not None:
            db_source.location = source.location
        if source.local_path is not None:
            db_source.local_path = source.local_path
        if source.added_by is not None:
            db_source.added_by = source.added_by
        if source.status is not None:
            if source.status not in SourceStatus.__members__:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid status")
            db_source.status = SourceStatus[source.status]

        await session.commit()


@router.delete("/{source_id}", tags=["source"])
async def delete(engine: EngineDep, source_id: int) -> None:
    async with engine.async_session() as session:
        source: Source = await session.scalar(select(Source).where(Source.id == source_id))
        if source is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Source not found")
        await session.delete(source)
        await session.commit()
