from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from aoq_factory.api.models.song import CreateSongRequest, SongResponse, UpdateSongRequest
from aoq_factory.database.models import Song
from aoq_factory.deps.engine import EngineDep


class SongService:
    def __init__(self, engine: EngineDep):
        self.engine = engine

    async def create(self, song: CreateSongRequest) -> bool:
        async with self.engine.async_session() as session:
            session.add(
                Song(
                    anime_id=song.anime_id,
                    category=song.category,
                    number=song.number,
                    song_artist=song.song_artist,
                    song_name=song.song_name,
                )
            )
            try:
                await session.commit()
                return True
            except IntegrityError:
                return False

    async def get_all(self) -> list[SongResponse]:
        async with self.engine.async_session() as session:
            songs = (await session.scalars(select(Song))).all()
            session.expunge_all()
        return [
            SongResponse(
                id=song.id,
                anime_id=song.anime_id,
                category=song.category,
                number=song.number,
                song_artist=song.song_artist,
                song_name=song.song_name,
            )
            for song in songs
        ]

    async def get_one(self, song_id: int) -> SongResponse | None:
        async with self.engine.async_session() as session:
            song = await session.scalar(select(Song).where(Song.id == song_id))
            if song:
                session.expunge(song)
                return SongResponse(
                    id=song.id,
                    anime_id=song.anime_id,
                    category=song.category,
                    number=song.number,
                    song_artist=song.song_artist,
                    song_name=song.song_name,
                )
            return None

    async def update(self, song_id: int, song: UpdateSongRequest) -> bool:
        async with self.engine.async_session() as session:
            db_song = await session.scalar(select(Song).where(Song.id == song_id))
            if not db_song:
                return False
            db_song.category = song.category
            db_song.number = song.number
            db_song.song_artist = song.song_artist
            db_song.song_name = song.song_name
            await session.commit()
            return True

    async def delete(self, song_id: int) -> bool:
        async with self.engine.async_session() as session:
            song = await session.scalar(select(Song).where(Song.id == song_id))
            if not song:
                return False
            await session.delete(song)
            await session.commit()
            return True
