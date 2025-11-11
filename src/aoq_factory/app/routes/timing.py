from typing import Optional

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from aoq_factory.app.deps.engine import EngineDep
from aoq_factory.database.models import Timing

router = APIRouter(prefix="/timings")


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
    guess_start: Optional[float] = None
    reveal_start: Optional[float] = None
    created_by: Optional[str] = None


@router.get("", tags=["timing"])
async def get_all(engine: EngineDep) -> list[TimingResponse]:
    async with engine.async_session() as session:
        timings: list[Timing] = (await session.scalars(select(Timing))).all()
        session.expunge_all()
    return [
        TimingResponse(
            id=timing.id,
            source_id=timing.source_id,
            guess_start=timing.guess_start,
            reveal_start=timing.reveal_start,
            created_by=timing.created_by,
        )
        for timing in timings
    ]


@router.get("/{timing_id}", tags=["timing"])
async def get(engine: EngineDep, timing_id: int) -> TimingResponse:
    async with engine.async_session() as session:
        timing: Timing = await session.scalar(select(Timing).where(Timing.id == timing_id))
        if timing is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Timing not found")
        session.expunge(timing)
    return TimingResponse(
        id=timing.id,
        source_id=timing.source_id,
        guess_start=timing.guess_start,
        reveal_start=timing.reveal_start,
        created_by=timing.created_by,
    )


@router.post("", tags=["timing"], status_code=status.HTTP_201_CREATED)
async def create(engine: EngineDep, timing: CreateTimingRequest) -> None:
    async with engine.async_session() as session:
        session.add(
            Timing(
                source_id=timing.source_id,
                guess_start=timing.guess_start,
                reveal_start=timing.reveal_start,
                created_by=timing.created_by,
            )
        )
        try:
            await session.commit()
        except IntegrityError as e:
            error_str = str(e.orig).lower()
            if "fk_timings_source_id_sources" in error_str:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Source not found") from e
            raise


@router.put("/{timing_id}", tags=["timing"])
async def update(engine: EngineDep, timing_id: int, timing: UpdateTimingRequest) -> None:
    async with engine.async_session() as session:
        db_timing: Timing = await session.scalar(select(Timing).where(Timing.id == timing_id))
        if db_timing is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Timing not found")

        if timing.guess_start is not None:
            db_timing.guess_start = timing.guess_start
        if timing.reveal_start is not None:
            db_timing.reveal_start = timing.reveal_start
        if timing.created_by is not None:
            db_timing.created_by = timing.created_by

        await session.commit()


@router.delete("/{timing_id}", tags=["timing"])
async def delete(engine: EngineDep, timing_id: int) -> None:
    async with engine.async_session() as session:
        timing: Timing = await session.scalar(select(Timing).where(Timing.id == timing_id))
        if timing is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Timing not found")
        await session.delete(timing)
        await session.commit()
