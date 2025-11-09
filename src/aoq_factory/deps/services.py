from typing import Annotated

from fastapi import Depends

from aoq_factory.services.anime_service import AnimeService
from aoq_factory.services.level_service import LevelService
from aoq_factory.services.song_service import SongService
from aoq_factory.services.source_service import SourceService
from aoq_factory.services.timing_service import TimingService

from .engine import EngineDep


def get_anime_service(engine: EngineDep) -> AnimeService:
    return AnimeService(engine)


def get_song_service(engine: EngineDep) -> SongService:
    return SongService(engine)


def get_source_service(engine: EngineDep) -> SourceService:
    return SourceService(engine)


def get_timing_service(engine: EngineDep) -> TimingService:
    return TimingService(engine)


def get_level_service(engine: EngineDep) -> LevelService:
    return LevelService(engine)


AnimeServiceDep = Annotated[AnimeService, Depends(get_anime_service)]
SongServiceDep = Annotated[SongService, Depends(get_song_service)]
SourceServiceDep = Annotated[SourceService, Depends(get_source_service)]
TimingServiceDep = Annotated[TimingService, Depends(get_timing_service)]
LevelServiceDep = Annotated[LevelService, Depends(get_level_service)]
