from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status

from aoq_factory.api.models.anime import AnimeResponse, CreateAnimeRequest
from aoq_factory.services import AnimeService

router = APIRouter(prefix="/animes")


@router.get("", tags=["anime"])
async def get_all(anime_service: Annotated[AnimeService, Depends()]) -> list[AnimeResponse]:
    return await anime_service.get_all()


@router.post("", tags=["anime"], status_code=status.HTTP_201_CREATED)
async def create(anime_service: Annotated[AnimeService, Depends()], anime: CreateAnimeRequest) -> None:
    success = await anime_service.create(anime)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=f"Anime with such mal_id(={anime.mal_id}) already exists."
        )
