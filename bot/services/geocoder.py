from dataclasses import dataclass

import aiohttp

from bot.services.errors import ExternalServiceError
from bot.services.maps_link import Coordinates
from bot.services.retry import with_retries

GEOCODER_URL = "https://geocode-maps.yandex.ru/1.x/"


@dataclass(frozen=True)
class AddressInfo:
    address: str
    city: str


def _find_city(components: list[dict]) -> str:
    for component in components:
        if component.get("kind") == "locality":
            return component.get("name", "")
    return ""


async def resolve_address(coords: Coordinates, api_key: str) -> AddressInfo:
    params = {
        "apikey": api_key,
        "geocode": f"{coords.lon},{coords.lat}",
        "format": "json",
        "lang": "ru_RU",
        "results": "1",
    }

    async def attempt() -> AddressInfo:
        async with aiohttp.ClientSession() as session:
            async with session.get(GEOCODER_URL, params=params, timeout=aiohttp.ClientTimeout(total=10)) as resp:
                if resp.status != 200:
                    raise ExternalServiceError(f"geocoder http {resp.status}")
                data = await resp.json()

        members = data["response"]["GeoObjectCollection"]["featureMember"]
        if not members:
            raise ExternalServiceError("geocoder returned no results")

        meta = members[0]["GeoObject"]["metaDataProperty"]["GeocoderMetaData"]
        address = meta["text"]
        city = _find_city(meta["Address"]["Components"])
        return AddressInfo(address=address, city=city)

    return await with_retries(attempt)
