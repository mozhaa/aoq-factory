from typing import Optional

from pydantic import BaseModel

from aoq_factory.database.models import Category


class CreateSongRequest(BaseModel):
    anime_id: int
    category: Category  # TODO: accept category as str
    number: int
    song_artist: str
    song_name: str


class SongResponse(BaseModel):
    id: int
    anime_id: int
    category: Category
    number: int
    song_artist: str
    song_name: str


class UpdateSongRequest(BaseModel):
    category: Optional[Category] = None
    number: Optional[int] = None
    song_artist: Optional[str] = None
    song_name: Optional[str] = None
