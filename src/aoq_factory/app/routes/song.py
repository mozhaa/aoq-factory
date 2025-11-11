from typing import Optional

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from aoq_factory.app.deps.engine import EngineDep
from aoq_factory.database.models import Category, Song

router = APIRouter(prefix="/songs")


class CreateSongRequest(BaseModel):
    anime_id: int
    category: str
    number: int
    song_artist: str
    song_name: str


class SongResponse(BaseModel):
    id: int
    anime_id: int
    category: str
    number: int
    song_artist: str
    song_name: str


class UpdateSongRequest(BaseModel):
    category: Optional[str] = None
    number: Optional[int] = None
    song_artist: Optional[str] = None
    song_name: Optional[str] = None


@router.get("", tags=["song"])
async def get_all(engine: EngineDep) -> list[SongResponse]:
    async with engine.async_session() as session:
        songs: list[Song] = (await session.scalars(select(Song))).all()
        session.expunge_all()
    return [
        SongResponse(
            id=song.id,
            anime_id=song.anime_id,
            category=song.category.name,
            number=song.number,
            song_artist=song.song_artist,
            song_name=song.song_name,
        )
        for song in songs
    ]


@router.get("/{song_id}", tags=["song"])
async def get(engine: EngineDep, song_id: int) -> SongResponse:
    async with engine.async_session() as session:
        song: Song = await session.scalar(select(Song).where(Song.id == song_id))
        if song is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Song not found")
        session.expunge(song)
    return SongResponse(
        id=song.id,
        anime_id=song.anime_id,
        category=song.category.name,
        number=song.number,
        song_artist=song.song_artist,
        song_name=song.song_name,
    )


@router.post("", tags=["song"], status_code=status.HTTP_201_CREATED)
async def create(engine: EngineDep, song: CreateSongRequest) -> None:
    async with engine.async_session() as session:
        if song.category not in Category.__members__:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid category")
        session.add(
            Song(
                anime_id=song.anime_id,
                category=Category[song.category],
                number=song.number,
                song_artist=song.song_artist,
                song_name=song.song_name,
            )
        )
        try:
            await session.commit()
        except IntegrityError as e:
            error_str = str(e.orig).lower()
            if "uq_songs_anime_id" in error_str:
                raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Song already exists") from e
            elif "fk_songs_anime_id_animes" in error_str:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Anime not found") from e
            raise


@router.put("/{song_id}", tags=["song"])
async def update(engine: EngineDep, song_id: int, song: UpdateSongRequest) -> None:
    async with engine.async_session() as session:
        db_song: Song = await session.scalar(select(Song).where(Song.id == song_id))
        if db_song is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Song not found")

        if song.category is not None:
            if song.category not in Category.__members__:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid category")
            db_song.category = Category[song.category]
        if song.number is not None:
            db_song.number = song.number
        if song.song_artist is not None:
            db_song.song_artist = song.song_artist
        if song.song_name is not None:
            db_song.song_name = song.song_name

        await session.commit()


@router.delete("/{song_id}", tags=["song"])
async def delete(engine: EngineDep, song_id: int) -> None:
    async with engine.async_session() as session:
        song: Song = await session.scalar(select(Song).where(Song.id == song_id))
        if song is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Song not found")
        await session.delete(song)
        await session.commit()
