from typing import Any, Optional

import aiohttp
from aiolimiter import AsyncLimiter

from aoq_factory.config import get_settings

from ..utils import default_headers

base_url = "https://api.ids.moe"
headers = default_headers.copy()
headers["Authorization"] = f"Bearer {get_settings().idsmoe_api_key}"

rate_limiter = AsyncLimiter(get_settings().idsmoe_rate_limiter_max_rate, get_settings().idsmoe_rate_limiter_time_period)


async def get(id_: int, platform: str) -> Optional[dict[str, Any]]:
    async with rate_limiter:
        async with aiohttp.ClientSession(base_url=base_url, headers=headers) as session:
            async with session.get(f"/ids/{id_}?platform={platform}") as response:
                if response.ok:
                    return await response.json()
