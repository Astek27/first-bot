from dataclasses import dataclass

from bot.services.maps_link import Coordinates


@dataclass(frozen=True)
class AddressInfo:
    address: str
    city: str


async def resolve_address(coords: Coordinates) -> AddressInfo:
    # Stub — always Moscow, real Yandex Geocoder call lands in phase 4.
    return AddressInfo(address="Москва, Тверская улица, 1", city="Москва")
