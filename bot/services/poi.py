from dataclasses import dataclass

from bot.services.maps_link import Coordinates


@dataclass(frozen=True)
class PoiFact:
    category: str
    name: str
    distance_m: int


async def find_poi(coords: Coordinates) -> list[PoiFact]:
    # Stub — fixed facts, real Overpass query (metro/schools/kindergartens, 500-800m) lands in phase 4.
    return [
        PoiFact(category="metro", name="Тверская", distance_m=350),
        PoiFact(category="school", name="Школа №1", distance_m=420),
        PoiFact(category="kindergarten", name="Детский сад №5", distance_m=280),
    ]
