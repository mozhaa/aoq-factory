from typing import Any, Optional

from pydantic import BaseModel


class CreateSourceRequest(BaseModel):
    song_id: int
    location: dict[str, Any]
    local_path: Optional[str]


class SourceResponse(BaseModel):
    id: int
    song_id: int
    location: dict[str, Any]
    local_path: Optional[str]
    is_downloading: bool
    is_invalid: bool


class UpdateSourceRequest(BaseModel):
    location: dict[str, Any]
    local_path: Optional[str]
    is_downloading: bool
    is_invalid: bool
