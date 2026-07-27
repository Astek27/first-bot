import re
from dataclasses import dataclass
from urllib.parse import parse_qs, urlparse

import aiohttp

from bot.services.errors import ExternalServiceError
from bot.services.retry import with_retries

_URL_RE = re.compile(r"https?://\S+")

# Query params that can carry a point, and whether they spell it "lat,lon".
# ll= and whatshere[point]= are lon,lat; text= is the search query, which the
# mobile "share" button fills with lat,lon.
_COORD_PARAMS = (("ll", False), ("whatshere[point]", False), ("text", True))


@dataclass(frozen=True)
class Coordinates:
    lat: float
    lon: float


def extract_url(text: str) -> str | None:
    """Pull the link out of a message — sharing a place sends address + link."""
    match = _URL_RE.search(text)
    return match.group(0) if match else None


def _parse_pair(raw: str, *, lat_first: bool) -> Coordinates | None:
    parts = raw.split(",")
    if len(parts) != 2:
        return None
    try:
        first, second = float(parts[0]), float(parts[1])
    except ValueError:
        return None
    lat, lon = (first, second) if lat_first else (second, first)
    if not (-90 <= lat <= 90 and -180 <= lon <= 180):
        return None
    return Coordinates(lat=lat, lon=lon)


def _extract_coords(url: str) -> Coordinates | None:
    query = parse_qs(urlparse(url).query)
    for param, lat_first in _COORD_PARAMS:
        values = query.get(param)
        if not values:
            continue
        coords = _parse_pair(values[0], lat_first=lat_first)
        if coords is not None:
            return coords
    return None


async def resolve_link(url: str) -> Coordinates:
    async def attempt() -> Coordinates:
        coords = _extract_coords(url)
        if coords is not None:
            return coords

        async with aiohttp.ClientSession() as session:
            async with session.get(url, allow_redirects=True, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                final_url = str(resp.url)
        coords = _extract_coords(final_url)
        if coords is None:
            raise ExternalServiceError(f"no coordinates found in {final_url}")
        return coords

    return await with_retries(attempt)
