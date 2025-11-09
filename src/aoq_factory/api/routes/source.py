from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from aoq_factory.api.models.source import CreateSourceRequest, SourceResponse, UpdateSourceRequest
from aoq_factory.services import SourceService
from aoq_factory.services.exc import NoSuchSong, NoSuchSource

router = APIRouter(prefix="/sources")


@router.get("", tags=["source"])
async def get_all(source_service: Annotated[SourceService, Depends()]) -> list[SourceResponse]:
    return await source_service.get_all()


@router.get("/{source_id}", tags=["source"])
async def get_one(source_service: Annotated[SourceService, Depends()], source_id: int) -> SourceResponse:
    try:
        return await source_service.get_one(source_id)
    except NoSuchSource as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Source not found") from e


@router.post("", tags=["source"], status_code=status.HTTP_201_CREATED)
async def create(source_service: Annotated[SourceService, Depends()], source: CreateSourceRequest) -> None:
    try:
        await source_service.create(source)
    except NoSuchSong as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Song not found") from e


@router.put("/{source_id}", tags=["source"])
async def update(
    source_service: Annotated[SourceService, Depends()], source_id: int, source: UpdateSourceRequest
) -> None:
    try:
        await source_service.update(source_id, source)
    except NoSuchSource as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Source not found") from e


@router.delete("/{source_id}", tags=["source"])
async def delete(source_service: Annotated[SourceService, Depends()], source_id: int) -> None:
    try:
        await source_service.delete(source_id)
    except NoSuchSource as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Source not found") from e
