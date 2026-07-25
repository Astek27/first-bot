import asyncio
import logging
from typing import Awaitable, Callable, TypeVar

from bot.services.errors import ExternalServiceError

logger = logging.getLogger(__name__)

T = TypeVar("T")


async def with_retries(call: Callable[[], Awaitable[T]], *, attempts: int = 3, delay_s: float = 1.0) -> T:
    last_error: Exception | None = None
    for attempt in range(1, attempts + 1):
        try:
            return await call()
        except Exception as exc:
            last_error = exc
            logger.warning("attempt %s/%s failed: %s", attempt, attempts, exc)
            if attempt < attempts:
                await asyncio.sleep(delay_s)
    raise ExternalServiceError(str(last_error)) from last_error
