from pydantic import BaseModel


class CreateLevelRequest(BaseModel):
    song_id: int
    value: int
    created_by: str


class LevelResponse(BaseModel):
    id: int
    song_id: int
    value: int
    created_by: str


class UpdateLevelRequest(BaseModel):
    value: int
    created_by: str
