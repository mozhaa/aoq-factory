from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from aoq_factory.api.models.source import CreateSourceRequest, SourceResponse, UpdateSourceRequest
from aoq_factory.services import SourceService

router = APIRouter(prefix="/sources")


@router.get("", tags=["source"])
async def get_all(source_service: Annotated[SourceService, Depends()]) -> list[SourceResponse]:
    return await source_service.get_all()


@router.get("/{source_id}", tags=["source"])
async def get_one(source_service: Annotated[SourceService, Depends()], source_id: int) -> SourceResponse:
    source = await source_service.get_one(source_id)
    if not source:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Source not found")
    return source


@router.post("", tags=["source"], status_code=status.HTTP_201_CREATED)
async def create(source_service: Annotated[SourceService, Depends()], source: CreateSourceRequest) -> None:
    success = await source_service.create(source)
    if not success:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Source already exists")


@router.put("/{source_id}", tags=["source"])
async def update(
    source_service: Annotated[SourceService, Depends()], source_id: int, source: UpdateSourceRequest
) -> None:
    success = await source_service.update(source_id, source)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Source not found")


@router.delete("/{source_id}", tags=["source"])
async def delete(source_service: Annotated[SourceService, Depends()], source_id: int) -> None:
    success = await source_service.delete(source_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Source not found")
