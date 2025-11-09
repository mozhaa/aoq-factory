from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from aoq_factory.api.models.timing import CreateTimingRequest, TimingResponse, UpdateTimingRequest
from aoq_factory.services import TimingService

router = APIRouter(prefix="/timings")


@router.get("", tags=["timing"])
async def get_all(timing_service: Annotated[TimingService, Depends()]) -> list[TimingResponse]:
    return await timing_service.get_all()


@router.get("/{timing_id}", tags=["timing"])
async def get_one(timing_service: Annotated[TimingService, Depends()], timing_id: int) -> TimingResponse:
    timing = await timing_service.get_one(timing_id)
    if not timing:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Timing not found")
    return timing


@router.post("", tags=["timing"], status_code=status.HTTP_201_CREATED)
async def create(timing_service: Annotated[TimingService, Depends()], timing: CreateTimingRequest) -> None:
    success = await timing_service.create(timing)
    if not success:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Timing already exists")


@router.put("/{timing_id}", tags=["timing"])
async def update(
    timing_service: Annotated[TimingService, Depends()], timing_id: int, timing: UpdateTimingRequest
) -> None:
    success = await timing_service.update(timing_id, timing)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Timing not found")


@router.delete("/{timing_id}", tags=["timing"])
async def delete(timing_service: Annotated[TimingService, Depends()], timing_id: int) -> None:
    success = await timing_service.delete(timing_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Timing not found")
