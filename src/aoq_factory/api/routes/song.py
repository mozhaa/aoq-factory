from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from aoq_factory.api.models.song import CreateSongRequest, SongResponse, UpdateSongRequest
from aoq_factory.services import SongService
from aoq_factory.services.exc import NoSuchAnime, NoSuchSong, SongAlreadyExists

router = APIRouter(prefix="/songs")


@router.get("", tags=["song"])
async def get_all(song_service: Annotated[SongService, Depends()]) -> list[SongResponse]:
    return await song_service.get_all()


@router.get("/{song_id}", tags=["song"])
async def get_one(song_service: Annotated[SongService, Depends()], song_id: int) -> SongResponse:
    try:
        return await song_service.get_one(song_id)
    except NoSuchSong as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Song not found") from e


@router.post("", tags=["song"], status_code=status.HTTP_201_CREATED)
async def create(song_service: Annotated[SongService, Depends()], song: CreateSongRequest) -> None:
    try:
        await song_service.create(song)
    except SongAlreadyExists as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Song already exists") from e
    except NoSuchAnime as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Anime not found") from e


@router.put("/{song_id}", tags=["song"])
async def update(song_service: Annotated[SongService, Depends()], song_id: int, song: UpdateSongRequest) -> None:
    try:
        await song_service.update(song_id, song)
    except NoSuchSong as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Song not found") from e


@router.delete("/{song_id}", tags=["song"])
async def delete(song_service: Annotated[SongService, Depends()], song_id: int) -> None:
    try:
        await song_service.delete(song_id)
    except NoSuchSong as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Song not found") from e
