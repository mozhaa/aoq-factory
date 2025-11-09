from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from aoq_factory.api.models.timing import CreateTimingRequest, TimingResponse, UpdateTimingRequest
from aoq_factory.services import TimingService
from aoq_factory.services.exc import NoSuchSource, NoSuchTiming

router = APIRouter(prefix="/timings")


@router.get("", tags=["timing"])
async def get_all(timing_service: Annotated[TimingService, Depends()]) -> list[TimingResponse]:
    return await timing_service.get_all()


@router.get("/{timing_id}", tags=["timing"])
async def get_one(timing_service: Annotated[TimingService, Depends()], timing_id: int) -> TimingResponse:
    try:
        return await timing_service.get_one(timing_id)
    except NoSuchTiming as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Timing not found") from e


@router.post("", tags=["timing"], status_code=status.HTTP_201_CREATED)
async def create(timing_service: Annotated[TimingService, Depends()], timing: CreateTimingRequest) -> None:
    try:
        await timing_service.create(timing)
    except NoSuchSource as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Source not found") from e


@router.put("/{timing_id}", tags=["timing"])
async def update(
    timing_service: Annotated[TimingService, Depends()], timing_id: int, timing: UpdateTimingRequest
) -> None:
    try:
        await timing_service.update(timing_id, timing)
    except NoSuchTiming as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Timing not found") from e


@router.delete("/{timing_id}", tags=["timing"])
async def delete(timing_service: Annotated[TimingService, Depends()], timing_id: int) -> None:
    try:
        await timing_service.delete(timing_id)
    except NoSuchTiming as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Timing not found") from e
