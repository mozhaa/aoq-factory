from typing import Optional

from aiohttp import ClientSession

from aoq_factory.config import get_settings

from ..utils import default_headers
from ..zlib_memoize import zlib_memoize


@zlib_memoize(f"{get_settings().resources_dir}/anidb.sqlite3", key_creator=str)
async def get_page(anidb_id: int) -> Optional[str]:
    async with ClientSession() as session:
        async with session.get(f"https://anidb.net/anime/{anidb_id}", headers=default_headers) as response:
            if response.ok:
                return await response.text()
