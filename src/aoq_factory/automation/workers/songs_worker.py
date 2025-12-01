import asyncio
import logging

from sqlalchemy import ColumnElement, Select, func, select

from aoq_factory.animeapi import anidb
from aoq_factory.database.connection import Engine
from aoq_factory.database.models import Anime, AnimeStatus, Song, WorkerResult, WorkerResultStatus

logger = logging.getLogger(__name__)


class SongsWorker:
    name: str = "songs_worker"

    def __init__(self, engine: Engine, batch_size: int, interval: float) -> None:
        self.engine = engine
        self.batch_size = batch_size
        self.interval = interval

    def _transform_songs_to_dict(self, songs: list[Song]) -> dict[str, Song]:
        return {f"{song.category} {song.number}" for song in songs}

    async def run(self) -> None:
        while True:
            animes = await self._get_unprocessed_animes(self.batch_size)
            logger.info(f"found {len(animes)} unprocessed animes: {[anime.title_ro for anime in animes]}")
            for anime in animes:
                logger.info(f"processing {anime.title_ro} (id={anime.id}, mal_id={anime.mal_id})")
                await self._process_anime(anime)
            await asyncio.sleep(self.interval)

    async def _process_anime(self, anime: Anime) -> None:
        if not (await self._does_anime_need_processing(anime)):
            return

        try:
            songs = await self.get_songs(anime)
        except Exception as e:
            logger.warning(f"exception occured during song list extraction from anidb page: {e}")

            async with self.engine.async_session() as session:
                session.add(
                    WorkerResult(
                        worker_name=self.worker_name,
                        anime_id=anime.id,
                        status=WorkerResultStatus.FAIL_INVALID,
                    )
                )
                await session.commit()
                return

        async with self.engine.async_session() as session:
            # filter out existings songs
            existings_songs = await session.scalars(select(Song).where(Song.anime_id == anime.id))

            existing_songs_dict = self._transform_songs_to_dict(existings_songs)
            songs_dict = self._transform_songs_to_dict(songs)

            songs_to_add_dict = {k: v for k, v in songs_dict.items() if k not in existing_songs_dict}
            filtered_songs_dict = {k: v for k, v in songs_dict.items() if k in existing_songs_dict}

            logger.info(
                f"adding songs {list(songs_to_add_dict.keys())} "
                f"(found, but already exist {list(filtered_songs_dict.keys())})"
            )

            session.add_all(list(songs_to_add_dict.values()))
            session.add(
                WorkerResult(
                    worker_name=self.worker_name,
                    anime_id=anime.id,
                    status=WorkerResultStatus.SUCCESS,
                )
            )
            await session.commit()

    async def get_songs(self, anime: Anime) -> list[Song]:
        return (await anidb.Page.from_id(anime.id)).songs

    def _is_anime_processed_clause(self) -> ColumnElement:
        processed_anime_subquery = (
            select(WorkerResult.anime_id)
            .where(
                WorkerResult.worker_name == self.name,
                WorkerResult.anime_id.is_not(None),
                WorkerResult.status != WorkerResultStatus.FAIL_TEMPORARY,
            )
            .scalar_subquery()
        )

        return Anime.id.not_in(processed_anime_subquery)

    def _does_anime_need_processing_clause(self) -> ColumnElement:
        return Anime.status == AnimeStatus.NORMAL

    def _unprocessed_animes_stmt(self) -> Select:
        return (
            select(Anime)
            .where(self._does_anime_need_processing_clause(), self._is_anime_processed_clause())
            .order_by(Anime.created_at.desc())
        )

    async def _get_unprocessed_animes(self, limit: int) -> list[Anime]:
        async with self.engine.async_session() as session:
            stmt = self._unprocessed_animes_stmt().limit(limit)
            animes = (await session.scalars(stmt)).all()
            session.expunge_all()
        return animes

    async def _does_anime_need_processing(self, anime: Anime) -> bool:
        async with self.engine.async_session() as session:
            stmt = (
                select(func.count())
                .select_from(Anime)
                .where(self._does_anime_need_processing_clause(), Anime.id == anime.id)
            )
            count = await session.scalar(stmt)
            return count > 0
