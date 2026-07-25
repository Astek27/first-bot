from dataclasses import dataclass

from bot.services.poi import PoiFact


@dataclass(frozen=True)
class ListingInput:
    address: str
    poi: list[PoiFact]
    property_type: str
    rooms: str
    area: str
    floor: str
    renovation: str
    wishes: str | None


async def generate_listing(data: ListingInput) -> str:
    # Stub — templated text, real GigaChat prompt/call lands in phase 4.
    poi_lines = "\n".join(f"- {p.name} ({p.distance_m} м)" for p in data.poi)
    wishes_line = f"\n{data.wishes}" if data.wishes else ""
    return (
        f"Продаётся {data.property_type}, {data.rooms}, {data.area} м², "
        f"этаж {data.floor}, ремонт: {data.renovation}.\n"
        f"Адрес: {data.address}\n"
        f"Рядом:\n{poi_lines}"
        f"{wishes_line}"
    )
