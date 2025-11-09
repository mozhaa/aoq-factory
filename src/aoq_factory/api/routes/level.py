from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from aoq_factory.api.models.level import CreateLevelRequest, LevelResponse, UpdateLevelRequest
from aoq_factory.services import LevelService
from aoq_factory.services.exc import InvalidLevelValue, NoSuchLevel, NoSuchSong

router = APIRouter(prefix="/levels")


@router.get("", tags=["level"])
async def get_all(level_service: Annotated[LevelService, Depends()]) -> list[LevelResponse]:
    return await level_service.get_all()


@router.get("/{level_id}", tags=["level"])
async def get_one(level_service: Annotated[LevelService, Depends()], level_id: int) -> LevelResponse:
    try:
        return await level_service.get_one(level_id)
    except NoSuchLevel as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Level not found") from e


@router.post("", tags=["level"], status_code=status.HTTP_201_CREATED)
async def create(level_service: Annotated[LevelService, Depends()], level: CreateLevelRequest) -> None:
    try:
        await level_service.create(level)
    except NoSuchSong as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Song not found") from e
    except InvalidLevelValue as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Level value must be between 0 and 100"
        ) from e


@router.put("/{level_id}", tags=["level"])
async def update(level_service: Annotated[LevelService, Depends()], level_id: int, level: UpdateLevelRequest) -> None:
    try:
        await level_service.update(level_id, level)
    except NoSuchLevel as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Level not found") from e


@router.delete("/{level_id}", tags=["level"])
async def delete(level_service: Annotated[LevelService, Depends()], level_id: int) -> None:
    try:
        await level_service.delete(level_id)
    except NoSuchLevel as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Level not found") from e
