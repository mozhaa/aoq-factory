from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from aoq_factory.api.models.song import CreateSongRequest, SongResponse, UpdateSongRequest
from aoq_factory.database.models import Category, Song
from aoq_factory.deps.engine import EngineDep

from .exc import InvalidCategory, NoSuchAnime, NoSuchSong, SongAlreadyExists


class SongService:
    def __init__(self, engine: EngineDep):
        self.engine = engine

    async def create(self, song: CreateSongRequest) -> None:
        async with self.engine.async_session() as session:
            if song.category not in Category.__members__:
                raise InvalidCategory()
            session.add(
                Song(
                    anime_id=song.anime_id,
                    category=Category[song.category],
                    number=song.number,
                    song_artist=song.song_artist,
                    song_name=song.song_name,
                )
            )
            try:
                await session.commit()
            except IntegrityError as e:
                error_str = str(e.orig).lower()
                if "uq_songs_anime_id" in error_str:
                    raise SongAlreadyExists() from e
                elif "fk_songs_anime_id_animes" in error_str:
                    raise NoSuchAnime() from e
                raise

    async def get_all(self) -> list[SongResponse]:
        async with self.engine.async_session() as session:
            songs: list[Song] = (await session.scalars(select(Song))).all()
            session.expunge_all()
        return [
            SongResponse(
                id=song.id,
                anime_id=song.anime_id,
                category=song.category.name,
                number=song.number,
                song_artist=song.song_artist,
                song_name=song.song_name,
            )
            for song in songs
        ]

    async def get_one(self, song_id: int) -> SongResponse:
        async with self.engine.async_session() as session:
            song: Song = await session.scalar(select(Song).where(Song.id == song_id))
            if song is None:
                raise NoSuchSong()
            session.expunge(song)
        return SongResponse(
            id=song.id,
            anime_id=song.anime_id,
            category=song.category.name,
            number=song.number,
            song_artist=song.song_artist,
            song_name=song.song_name,
        )

    async def update(self, song_id: int, song: UpdateSongRequest) -> None:
        async with self.engine.async_session() as session:
            db_song: Song = await session.scalar(select(Song).where(Song.id == song_id))
            if db_song is None:
                raise NoSuchSong()

            if song.category is not None:
                if song.category not in Category.__members__:
                    raise InvalidCategory()
                db_song.category = Category[song.category]
            if song.number is not None:
                db_song.number = song.number
            if song.song_artist is not None:
                db_song.song_artist = song.song_artist
            if song.song_name is not None:
                db_song.song_name = song.song_name

            await session.commit()

    async def delete(self, song_id: int) -> None:
        async with self.engine.async_session() as session:
            song: Song = await session.scalar(select(Song).where(Song.id == song_id))
            if song is None:
                raise NoSuchSong()
            await session.delete(song)
            await session.commit()
