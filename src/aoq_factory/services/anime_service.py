from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from aoq_factory.api.models.anime import AnimeResponse, CreateAnimeRequest, UpdateAnimeRequest
from aoq_factory.database.models import Anime
from aoq_factory.deps.engine import EngineDep

from .exc import AnimeAlreadyExists, NoSuchAnime


class AnimeService:
    def __init__(self, engine: EngineDep):
        self.engine = engine

    async def create(self, anime: CreateAnimeRequest) -> None:
        async with self.engine.async_session() as session:
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
                    raise AnimeAlreadyExists() from e
                raise

    async def get_all(self) -> list[AnimeResponse]:
        async with self.engine.async_session() as session:
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

    async def get_one(self, mal_id: int) -> AnimeResponse:
        async with self.engine.async_session() as session:
            anime: Anime = await session.scalar(select(Anime).where(Anime.mal_id == mal_id))
            if anime is None:
                raise NoSuchAnime()
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

    async def update(self, mal_id: int, anime: UpdateAnimeRequest) -> None:
        async with self.engine.async_session() as session:
            db_anime: Anime = await session.scalar(select(Anime).where(Anime.mal_id == mal_id))
            if db_anime is None:
                raise NoSuchAnime()

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

    async def delete(self, mal_id: int) -> None:
        async with self.engine.async_session() as session:
            anime: Anime = await session.scalar(select(Anime).where(Anime.mal_id == mal_id))
            if anime is None:
                raise NoSuchAnime()
            await session.delete(anime)
            await session.commit()
