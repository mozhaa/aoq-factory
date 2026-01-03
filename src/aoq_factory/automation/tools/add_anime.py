from anime_utils.clients.anidb import AniDBScraper
from anime_utils.clients.idsmoe import IDsMoeClient

from aoq_factory.database.connection import get_engine
from aoq_factory.database.models import Anime, IDMapping, Platform


async def add_anime_by_anidb_id(anidb_id: int) -> None:
    async with IDsMoeClient() as idsmoe:
        ids = await idsmoe.get(anidb_id, "anidb")
    if ids is None:
        raise ValueError(f"failed to fetch ids from ids.moe: {anidb_id=}")

    async with AniDBScraper() as anidb:
        main_info = await anidb.get_main_info(anidb_id)
    if main_info is None:
        raise ValueError(f"failed to fetch main info from anidb: {anidb_id=}")

    ids_by_platform: dict[Platform, int] = {Platform.ANIDB: anidb_id}
    for platform, key in (
        (Platform.MAL, "myanimelist"),
        (Platform.ANIMENEWSNETWORK, "animenewsnetwork"),
        (Platform.ANILIST, "anilist"),
    ):
        if key in ids:
            ids_by_platform[platform] = ids[key]

    async with get_engine().async_session() as session:
        anime = Anime(title_ro=main_info["main_title"])
        session.add(anime)
        await session.flush()
        for platform, value in ids_by_platform.items():
            session.add(IDMapping(anime_id=anime.id, value=value, platform=platform))
        await session.commit()
