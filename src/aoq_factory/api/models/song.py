from typing import Optional

from pydantic import BaseModel


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
