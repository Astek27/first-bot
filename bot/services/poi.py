import math
from dataclasses import dataclass
from urllib.parse import urlparse

import aiohttp

from bot.services.errors import ExternalServiceError
from bot.services.maps_link import Coordinates
from bot.services.retry import with_retries

# Public Overpass instances go 504 under load independently of each other, so a
# retry is only worth anything if it lands on a different host — one attempt each.
OVERPASS_MIRRORS = (
    "https://overpass-api.de/api/interpreter",
    "https://overpass.kumi.systems/api/interpreter",
    "https://overpass.private.coffee/api/interpreter",
    "https://maps.mail.ru/osm/tools/overpass/api/interpreter",
)
RADIUS_M = 800

# Resolves the open question from CLAUDE.md: metro = subway station nodes,
# schools/kindergartens = their standard OSM amenity tags.
CATEGORY_QUERIES = {
    "metro": '["railway"="station"]["station"="subway"]',
    "school": '["amenity"="school"]',
    "kindergarten": '["amenity"="kindergarten"]',
}


@dataclass(frozen=True)
class PoiFact:
    category: str
    name: str
    distance_m: int


def _build_query(coords: Coordinates) -> str:
    around = f"(around:{RADIUS_M},{coords.lat},{coords.lon})"
    # nwr, not node: in Moscow most schools and kindergartens are mapped as
    # building/grounds polygons (way/relation). A node-only query found 2 of the
    # 10 schools around a test point, so "nearest school" was picked from a
    # near-random subset. out center gives polygons a centroid to measure from.
    statements = "".join(f"nwr{tags}{around};" for tags in CATEGORY_QUERIES.values())
    return f"[out:json][timeout:15];({statements});out center;"


def _distance_m(a: Coordinates, b_lat: float, b_lon: float) -> int:
    earth_radius_m = 6371000
    lat1, lat2 = math.radians(a.lat), math.radians(b_lat)
    dlat = math.radians(b_lat - a.lat)
    dlon = math.radians(b_lon - a.lon)
    h = math.sin(dlat / 2) ** 2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon / 2) ** 2
    return round(2 * earth_radius_m * math.asin(math.sqrt(h)))


def _element_coords(element: dict) -> tuple[float, float] | None:
    """Nodes carry lat/lon directly; ways and relations get it under `center`."""
    if "lat" in element and "lon" in element:
        return element["lat"], element["lon"]
    center = element.get("center")
    if center and "lat" in center and "lon" in center:
        return center["lat"], center["lon"]
    return None


def _category_of(tags: dict) -> str | None:
    if tags.get("railway") == "station" and tags.get("station") == "subway":
        return "metro"
    if tags.get("amenity") == "school":
        return "school"
    if tags.get("amenity") == "kindergarten":
        return "kindergarten"
    return None


async def find_poi(coords: Coordinates) -> list[PoiFact]:
    query = _build_query(coords)

    mirrors = iter(OVERPASS_MIRRORS)

    async def attempt() -> list[PoiFact]:
        url = next(mirrors)
        host = urlparse(url).netloc
        async with aiohttp.ClientSession() as session:
            async with session.post(
                url, data={"data": query}, timeout=aiohttp.ClientTimeout(total=8)
            ) as resp:
                if resp.status != 200:
                    raise ExternalServiceError(f"overpass http {resp.status} ({host})")
                data = await resp.json()

        by_category: dict[str, PoiFact] = {}
        for element in data.get("elements", []):
            tags = element.get("tags", {})
            category = _category_of(tags)
            point = _element_coords(element)
            if category is None or point is None:
                continue
            fact = PoiFact(
                category=category,
                name=tags.get("name", "Без названия"),
                distance_m=_distance_m(coords, point[0], point[1]),
            )
            current = by_category.get(category)
            if current is None or fact.distance_m < current.distance_m:
                by_category[category] = fact
        return sorted(by_category.values(), key=lambda f: f.distance_m)

    return await with_retries(attempt, attempts=len(OVERPASS_MIRRORS), delay_s=0.5)
