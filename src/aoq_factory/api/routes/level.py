from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from aoq_factory.api.models.level import CreateLevelRequest, LevelResponse, UpdateLevelRequest
from aoq_factory.services import LevelService

router = APIRouter(prefix="/levels")


@router.get("", tags=["level"])
async def get_all(level_service: Annotated[LevelService, Depends()]) -> list[LevelResponse]:
    return await level_service.get_all()


@router.get("/{level_id}", tags=["level"])
async def get_one(level_service: Annotated[LevelService, Depends()], level_id: int) -> LevelResponse:
    level = await level_service.get_one(level_id)
    if not level:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Level not found")
    return level


@router.post("", tags=["level"], status_code=status.HTTP_201_CREATED)
async def create(level_service: Annotated[LevelService, Depends()], level: CreateLevelRequest) -> None:
    success = await level_service.create(level)
    if not success:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Level already exists")


@router.put("/{level_id}", tags=["level"])
async def update(level_service: Annotated[LevelService, Depends()], level_id: int, level: UpdateLevelRequest) -> None:
    success = await level_service.update(level_id, level)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Level not found")


@router.delete("/{level_id}", tags=["level"])
async def delete(level_service: Annotated[LevelService, Depends()], level_id: int) -> None:
    success = await level_service.delete(level_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Level not found")
