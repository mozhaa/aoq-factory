from typing import Optional

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from aoq_factory.app.deps.engine import EngineDep
from aoq_factory.database.models import Anime

router = APIRouter(prefix="/animes")


class CreateAnimeRequest(BaseModel):
    mal_id: int
    title_ro: str
    poster_url: str
    poster_thumb_url: str
    release_year: int


class AnimeResponse(BaseModel):
    mal_id: int
    title_ro: str
    poster_url: str
    poster_thumb_url: str
    release_year: int
    is_blacklisted: bool
    is_finalized: bool


class UpdateAnimeRequest(BaseModel):
    title_ro: Optional[str] = None
    poster_url: Optional[str] = None
    poster_thumb_url: Optional[str] = None
    release_year: Optional[int] = None
    is_blacklisted: Optional[bool] = None
    is_finalized: Optional[bool] = None


@router.get("", tags=["anime"])
async def get_all(engine: EngineDep) -> list[AnimeResponse]:
    async with engine.async_session() as session:
        animes: list[Anime] = (await session.scalars(select(Anime))).all()
        session.expunge_all()
    return [
        AnimeResponse(
            mal_id=anime.mal_id,
            title_ro=anime.title_ro,
            poster_url=anime.poster_url,
            poster_thumb_url=anime.poster_thumb_url,
            release_year=anime.release_year,
            is_blacklisted=anime.is_blacklisted,
            is_finalized=anime.is_finalized,
        )
        for anime in animes
    ]


@router.get("/{mal_id}", tags=["anime"])
async def get(engine: EngineDep, mal_id: int) -> AnimeResponse:
    async with engine.async_session() as session:
        anime: Anime = await session.scalar(select(Anime).where(Anime.mal_id == mal_id))
        if anime is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Anime not found")
        session.expunge(anime)
    return AnimeResponse(
        mal_id=anime.mal_id,
        title_ro=anime.title_ro,
        poster_url=anime.poster_url,
        poster_thumb_url=anime.poster_thumb_url,
        release_year=anime.release_year,
        is_blacklisted=anime.is_blacklisted,
        is_finalized=anime.is_finalized,
    )


@router.post("", tags=["anime"], status_code=status.HTTP_201_CREATED)
async def create(engine: EngineDep, anime: CreateAnimeRequest) -> None:
    async with engine.async_session() as session:
        session.add(
            Anime(
                mal_id=anime.mal_id,
                title_ro=anime.title_ro,
                poster_url=anime.poster_url,
                poster_thumb_url=anime.poster_thumb_url,
                release_year=anime.release_year,
            )
        )
        try:
            await session.commit()
        except IntegrityError as e:
            error_str = str(e.orig).lower()
            if "pk_animes" in error_str:
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT,
                    detail=f"Anime with such mal_id(={anime.mal_id}) already exists.",
                ) from e
            raise


@router.put("/{mal_id}", tags=["anime"])
async def update(engine: EngineDep, mal_id: int, anime: UpdateAnimeRequest) -> None:
    async with engine.async_session() as session:
        db_anime: Anime = await session.scalar(select(Anime).where(Anime.mal_id == mal_id))
        if db_anime is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Anime not found")

        if anime.title_ro is not None:
            db_anime.title_ro = anime.title_ro
        if anime.poster_url is not None:
            db_anime.poster_url = anime.poster_url
        if anime.poster_thumb_url is not None:
            db_anime.poster_thumb_url = anime.poster_thumb_url
        if anime.release_year is not None:
            db_anime.release_year = anime.release_year
        if anime.is_blacklisted is not None:
            db_anime.is_blacklisted = anime.is_blacklisted
        if anime.is_finalized is not None:
            db_anime.is_finalized = anime.is_finalized

        await session.commit()


@router.delete("/{mal_id}", tags=["anime"])
async def delete(engine: EngineDep, mal_id: int) -> None:
    async with engine.async_session() as session:
        anime: Anime = await session.scalar(select(Anime).where(Anime.mal_id == mal_id))
        if anime is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Anime not found")
        await session.delete(anime)
        await session.commit()
