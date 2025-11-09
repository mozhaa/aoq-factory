from pydantic import BaseModel


class CreateTimingRequest(BaseModel):
    source_id: int
    guess_start: float
    reveal_start: float
    created_by: str


class TimingResponse(BaseModel):
    id: int
    source_id: int
    guess_start: float
    reveal_start: float
    created_by: str


class UpdateTimingRequest(BaseModel):
    guess_start: float
    reveal_start: float
    created_by: str
