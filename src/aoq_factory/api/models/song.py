from pydantic import BaseModel

from aoq_factory.database.models import Category


class CreateSongRequest(BaseModel):
    anime_id: int
    category: Category
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
    category: Category  # TODO: make nullable for partial update
    number: int
    song_artist: str
    song_name: str
