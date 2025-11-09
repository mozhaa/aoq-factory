from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from aoq_factory.api.models.timing import CreateTimingRequest, TimingResponse, UpdateTimingRequest
from aoq_factory.database.models import Timing
from aoq_factory.deps.engine import EngineDep


class TimingService:
    def __init__(self, engine: EngineDep):
        self.engine = engine

    async def create(self, timing: CreateTimingRequest) -> bool:
        async with self.engine.async_session() as session:
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
                return True
            except IntegrityError:
                return False

    async def get_all(self) -> list[TimingResponse]:
        async with self.engine.async_session() as session:
            timings = (await session.scalars(select(Timing))).all()
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

    async def get_one(self, timing_id: int) -> TimingResponse | None:
        async with self.engine.async_session() as session:
            timing = await session.scalar(select(Timing).where(Timing.id == timing_id))
            if timing:
                session.expunge(timing)
                return TimingResponse(
                    id=timing.id,
                    source_id=timing.source_id,
                    guess_start=timing.guess_start,
                    reveal_start=timing.reveal_start,
                    created_by=timing.created_by,
                )
            return None

    async def update(self, timing_id: int, timing: UpdateTimingRequest) -> bool:
        async with self.engine.async_session() as session:
            db_timing = await session.scalar(select(Timing).where(Timing.id == timing_id))
            if not db_timing:
                return False
            db_timing.guess_start = timing.guess_start
            db_timing.reveal_start = timing.reveal_start
            db_timing.created_by = timing.created_by
            await session.commit()
            return True

    async def delete(self, timing_id: int) -> bool:
        async with self.engine.async_session() as session:
            timing = await session.scalar(select(Timing).where(Timing.id == timing_id))
            if not timing:
                return False
            await session.delete(timing)
            await session.commit()
            return True
