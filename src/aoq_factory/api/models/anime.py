from typing import Optional

from pydantic import BaseModel


class CreateAnimeRequest(BaseModel):
    mal_id: int
    title_ro: str
    poster_url: str
    poster_thumb_url: str
    release_year: int


class AnimeResponse(BaseModel):
    mal_id: int
    title_ro: str
    poster_url: str
    poster_thumb_url: str
    release_year: int
    is_blacklisted: bool
    is_finalized: bool


class UpdateAnimeRequest(BaseModel):
    title_ro: Optional[str] = None
    poster_url: Optional[str] = None
    poster_thumb_url: Optional[str] = None
    release_year: Optional[int] = None
    is_blacklisted: Optional[bool] = None
    is_finalized: Optional[bool] = None
