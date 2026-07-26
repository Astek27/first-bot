import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    tg_bot_token: str
    yandex_geocoder_api_key: str
    gigachat_api_key: str
    tg_api_base_url: str


def load_settings() -> Settings:
    token = os.environ.get("TG_BOT_TOKEN", "")
    if not token:
        raise RuntimeError("TG_BOT_TOKEN is not set (see .env.example)")

    return Settings(
        tg_bot_token=token,
        yandex_geocoder_api_key=os.environ.get("YANDEX_GEOCODER_API_KEY", ""),
        gigachat_api_key=os.environ.get("GIGACHAT_API_KEY", ""),
        tg_api_base_url=os.environ.get("TG_API_BASE_URL", ""),
    )
