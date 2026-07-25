import time
import uuid
from dataclasses import dataclass

import aiohttp

from bot.services.errors import ExternalServiceError
from bot.services.poi import PoiFact
from bot.services.retry import with_retries

OAUTH_URL = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"
CHAT_URL = "https://gigachat.devices.sberbank.ru/api/v1/chat/completions"
MODEL = "GigaChat"

SYSTEM_PROMPT = (
    "Ты — копирайтер по недвижимости. Пиши текст объявления о продаже по "
    "предоставленным фактам. Не придумывай данные, которых нет во входных "
    "фактах (объекты инфраструктуры, метраж и т.д.)."
)

# GigaChat use Russian state (Mincifry) root CA that is often untrusted by
# default on non-RU systems; skipping verification is the common pragmatic
# workaround for MVP. See CLAUDE.md known pitfalls.
_SSL_VERIFY = False

_cached_token: str | None = None
_cached_token_expires_at: float = 0.0


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


async def _fetch_access_token(auth_key: str) -> tuple[str, float]:
    headers = {
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json",
        "RqUID": str(uuid.uuid4()),
        "Authorization": f"Basic {auth_key}",
    }
    async with aiohttp.ClientSession() as session:
        async with session.post(
            OAUTH_URL,
            headers=headers,
            data={"scope": "GIGACHAT_API_PERS"},
            timeout=aiohttp.ClientTimeout(total=10),
            ssl=_SSL_VERIFY,
        ) as resp:
            if resp.status != 200:
                raise ExternalServiceError(f"gigachat oauth http {resp.status}")
            data = await resp.json()
    # expires_at is a server-side unix timestamp in ms; refresh a bit early.
    return data["access_token"], data["expires_at"] / 1000 - 30


async def _get_access_token(auth_key: str) -> str:
    global _cached_token, _cached_token_expires_at
    if _cached_token and time.time() < _cached_token_expires_at:
        return _cached_token

    async def attempt() -> tuple[str, float]:
        return await _fetch_access_token(auth_key)

    token, expires_at = await with_retries(attempt)
    _cached_token, _cached_token_expires_at = token, expires_at
    return token


def _build_prompt(data: ListingInput) -> str:
    poi_lines = "\n".join(f"- {p.category}: {p.name}, {p.distance_m} м" for p in data.poi) or "нет данных"
    wishes_line = f"\nПожелания риелтора: {data.wishes}" if data.wishes else ""
    return (
        f"Тип объекта: {data.property_type}\n"
        f"Комнат: {data.rooms}\n"
        f"Площадь: {data.area} м²\n"
        f"Этаж: {data.floor}\n"
        f"Ремонт: {data.renovation}\n"
        f"Адрес: {data.address}\n"
        f"Рядом:\n{poi_lines}"
        f"{wishes_line}"
    )


async def generate_listing(data: ListingInput, api_key: str) -> str:
    token = await _get_access_token(api_key)

    async def attempt() -> str:
        payload = {
            "model": MODEL,
            "messages": [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": _build_prompt(data)},
            ],
        }
        headers = {"Accept": "application/json", "Authorization": f"Bearer {token}"}
        async with aiohttp.ClientSession() as session:
            async with session.post(
                CHAT_URL,
                headers=headers,
                json=payload,
                timeout=aiohttp.ClientTimeout(total=30),
                ssl=_SSL_VERIFY,
            ) as resp:
                if resp.status != 200:
                    raise ExternalServiceError(f"gigachat chat http {resp.status}")
                result = await resp.json()
        return result["choices"][0]["message"]["content"]

    return await with_retries(attempt, attempts=1)
