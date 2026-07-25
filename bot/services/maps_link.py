from dataclasses import dataclass
from urllib.parse import parse_qs, urlparse

import aiohttp

from bot.services.errors import ExternalServiceError
from bot.services.retry import with_retries


@dataclass(frozen=True)
class Coordinates:
    lat: float
    lon: float


def _extract_ll(url: str) -> Coordinates | None:
    query = parse_qs(urlparse(url).query)
    ll = query.get("ll")
    if not ll:
        return None
    lon_str, lat_str = ll[0].split(",")
    return Coordinates(lat=float(lat_str), lon=float(lon_str))


async def resolve_link(url: str) -> Coordinates:
    async def attempt() -> Coordinates:
        async with aiohttp.ClientSession() as session:
            async with session.get(url, allow_redirects=True, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                final_url = str(resp.url)
        coords = _extract_ll(final_url) or _extract_ll(url)
        if coords is None:
            raise ExternalServiceError(f"no ll= coordinates found in {final_url}")
        return coords

    return await with_retries(attempt)
