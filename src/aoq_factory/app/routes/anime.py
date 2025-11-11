from typing import Optional

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from aoq_factory.app.deps.engine import EngineDep
from aoq_factory.database.models import Anime, AnimeStatus

router = APIRouter(prefix="/animes")


class CreateAnimeRequest(BaseModel):
    mal_id: int
    title_ro: str
    poster_url: str
    release_year: int
    status: Optional[str] = None


class AnimeResponse(BaseModel):
    mal_id: int
    title_ro: str
    poster_url: str
    release_year: int
    status: str


class UpdateAnimeRequest(BaseModel):
    title_ro: Optional[str] = None
    poster_url: Optional[str] = None
    release_year: Optional[int] = None
    status: Optional[str] = None


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
            release_year=anime.release_year,
            status=anime.status.name,
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
        release_year=anime.release_year,
        status=anime.status.name,
    )


@router.post("", tags=["anime"], status_code=status.HTTP_201_CREATED)
async def create(engine: EngineDep, anime: CreateAnimeRequest) -> None:
    async with engine.async_session() as session:
        status_enum = AnimeStatus.NORMAL
        if anime.status is not None:
            if anime.status not in AnimeStatus.__members__:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid status")
            status_enum = AnimeStatus[anime.status]

        session.add(
            Anime(
                mal_id=anime.mal_id,
                title_ro=anime.title_ro,
                poster_url=anime.poster_url,
                release_year=anime.release_year,
                status=status_enum,
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
        if anime.release_year is not None:
            db_anime.release_year = anime.release_year
        if anime.status is not None:
            if anime.status not in AnimeStatus.__members__:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid status")
            db_anime.status = AnimeStatus[anime.status]

        await session.commit()


@router.delete("/{mal_id}", tags=["anime"])
async def delete(engine: EngineDep, mal_id: int) -> None:
    async with engine.async_session() as session:
        anime: Anime = await session.scalar(select(Anime).where(Anime.mal_id == mal_id))
        if anime is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Anime not found")
        await session.delete(anime)
        await session.commit()
