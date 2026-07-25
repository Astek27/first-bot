from dataclasses import dataclass


@dataclass(frozen=True)
class Coordinates:
    lat: float
    lon: float


async def resolve_link(url: str) -> Coordinates:
    # Stub — ignores url, real parsing of short/ll=/oid= links lands in phase 4.
    return Coordinates(lat=55.751244, lon=37.618423)
