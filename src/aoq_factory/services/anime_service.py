from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from aoq_factory.api.models.anime import AnimeResponse, CreateAnimeRequest
from aoq_factory.database.models import Anime
from aoq_factory.deps import EngineDep


class AnimeService:
    def __init__(self, engine: EngineDep):
        self.engine = engine

    async def create(self, anime: CreateAnimeRequest) -> bool:
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
                return True
            except IntegrityError:
                return False

    async def get_all(self) -> list[AnimeResponse]:
        async with self.engine.async_session() as session:
            animes = (await session.scalars(select(Anime))).all()
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
