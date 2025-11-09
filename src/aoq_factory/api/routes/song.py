from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from aoq_factory.api.models.song import CreateSongRequest, SongResponse, UpdateSongRequest
from aoq_factory.services import SongService

router = APIRouter(prefix="/songs")


@router.get("", tags=["song"])
async def get_all(song_service: Annotated[SongService, Depends()]) -> list[SongResponse]:
    return await song_service.get_all()


@router.get("/{song_id}", tags=["song"])
async def get_one(song_service: Annotated[SongService, Depends()], song_id: int) -> SongResponse:
    song = await song_service.get_one(song_id)
    if not song:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Song not found")
    return song


@router.post("", tags=["song"], status_code=status.HTTP_201_CREATED)
async def create(song_service: Annotated[SongService, Depends()], song: CreateSongRequest) -> None:
    success = await song_service.create(song)
    if not success:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Song already exists")


@router.put("/{song_id}", tags=["song"])
async def update(song_service: Annotated[SongService, Depends()], song_id: int, song: UpdateSongRequest) -> None:
    success = await song_service.update(song_id, song)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Song not found")


@router.delete("/{song_id}", tags=["song"])
async def delete(song_service: Annotated[SongService, Depends()], song_id: int) -> None:
    success = await song_service.delete(song_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Song not found")
