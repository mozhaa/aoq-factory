from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from aoq_factory.api.models.anime import AnimeResponse, CreateAnimeRequest, UpdateAnimeRequest
from aoq_factory.services import AnimeService

router = APIRouter(prefix="/animes")


@router.get("", tags=["anime"])
async def get_all(anime_service: Annotated[AnimeService, Depends()]) -> list[AnimeResponse]:
    return await anime_service.get_all()


@router.get("/{mal_id}", tags=["anime"])
async def get_one(anime_service: Annotated[AnimeService, Depends()], mal_id: int) -> AnimeResponse:
    anime = await anime_service.get_one(mal_id)
    if not anime:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Anime not found")
    return anime


@router.post("", tags=["anime"], status_code=status.HTTP_201_CREATED)
async def create(anime_service: Annotated[AnimeService, Depends()], anime: CreateAnimeRequest) -> None:
    success = await anime_service.create(anime)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=f"Anime with such mal_id(={anime.mal_id}) already exists."
        )


@router.put("/{mal_id}", tags=["anime"])
async def update(anime_service: Annotated[AnimeService, Depends()], mal_id: int, anime: UpdateAnimeRequest) -> None:
    success = await anime_service.update(mal_id, anime)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Anime not found")


@router.delete("/{mal_id}", tags=["anime"])
async def delete(anime_service: Annotated[AnimeService, Depends()], mal_id: int) -> None:
    success = await anime_service.delete(mal_id)
    if not success:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Anime not found")
