import enum
from datetime import datetime
from typing import Any, ClassVar, List, Optional, Type

import sqlalchemy.types as types
from sqlalchemy import ForeignKey, String, UniqueConstraint, func
from sqlalchemy.dialects import postgresql
from sqlalchemy.ext.asyncio import AsyncAttrs
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.schema import MetaData


def keyvalgen(obj):
    """Generate attr name/val pairs, filtering out SQLA attrs."""
    excl = ("_sa_adapter", "_sa_instance_state")
    for k, v in vars(obj).items():
        if not k.startswith("_") and not any(hasattr(v, a) for a in excl):
            yield k, v


convention: dict[str, str] = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}


class Base(AsyncAttrs, DeclarativeBase):
    created_at: Mapped[datetime] = mapped_column(server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(server_default=func.now(), onupdate=func.now())

    metadata: ClassVar[MetaData] = MetaData(naming_convention=convention)
    type_annotation_map: ClassVar[dict[Type, types.TypeEngine]] = {
        datetime: types.TIMESTAMP(timezone=True),
        list[str]: postgresql.ARRAY(String, dimensions=1, zero_indexes=True),
        list[list[str]]: postgresql.ARRAY(String, dimensions=2, zero_indexes=True),
        dict[str, Any]: types.JSON(),
    }

    def __repr__(self):
        params = ", ".join(f"{k}={v}" for k, v in keyvalgen(self))
        return f"{self.__class__.__name__}({params})"


class BaseWithID(Base):
    __abstract__ = True

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)


class Anime(Base):
    __tablename__ = "animes"

    mal_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    title_ro: Mapped[str]
    poster_url: Mapped[str]
    poster_thumb_url: Mapped[str]
    release_year: Mapped[int]
    is_blacklisted: Mapped[bool] = mapped_column(default=False)
    is_finalized: Mapped[bool] = mapped_column(default=False)

    infos: Mapped[List["AnimeInfo"]] = relationship(back_populates="anime", cascade="all, delete")
    songs: Mapped[List["Song"]] = relationship(back_populates="anime", cascade="all, delete")


class AnimeInfo(BaseWithID):
    __tablename__ = "anime_infos"

    anime_id: Mapped[Anime] = mapped_column(ForeignKey(column="animes.mal_id"))
    source: Mapped[str]
    data: Mapped[dict[str, Any]]

    anime: Mapped[Anime] = relationship(back_populates="infos")


class Category(enum.Enum):
    Opening = enum.auto()
    Ending = enum.auto()


class Song(BaseWithID):
    __tablename__ = "songs"

    anime_id: Mapped[int] = mapped_column(ForeignKey("animes.mal_id"))
    category: Mapped[Category] = mapped_column(types.Enum(Category))
    number: Mapped[int]
    song_artist: Mapped[str] = mapped_column(default="")
    song_name: Mapped[str] = mapped_column(default="")

    anime: Mapped[Anime] = relationship(back_populates="songs")
    sources: Mapped[List["SongSource"]] = relationship(back_populates="song", cascade="all, delete")

    __table_args__ = (UniqueConstraint("anime_id", "category", "number"),)


class SongSource(BaseWithID):
    __tablename__ = "song_sources"

    song_id: Mapped[int] = mapped_column(ForeignKey("songs.id"))
    location: Mapped[dict[str, Any]]
    local_path: Mapped[Optional[str]]
    is_downloading: Mapped[bool] = mapped_column(default=False)
    is_invalid: Mapped[bool] = mapped_column(default=False)

    song: Mapped[Anime] = relationship(back_populates="sources")
