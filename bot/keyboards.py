from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

TYPE_OPTIONS = [
    ("Квартира", "apartment"),
    ("Дом", "house"),
    ("Коммерция", "commercial"),
]

ROOMS_OPTIONS = [
    ("Студия", "studio"),
    ("1", "1"),
    ("2", "2"),
    ("3", "3"),
    ("4+", "4plus"),
]

RENOVATION_OPTIONS = [
    ("Черновая", "raw"),
    ("Косметический", "cosmetic"),
    ("Евро", "euro"),
    ("Дизайнерский", "design"),
]

RESULT_OPTIONS = [
    ("Сгенерировать заново", "regenerate"),
    ("Начать заново", "restart"),
]


def _build(prefix: str, options: list[tuple[str, str]]) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for label, value in options:
        builder.add(InlineKeyboardButton(text=label, callback_data=f"{prefix}:{value}"))
    builder.adjust(2)
    return builder.as_markup()


def type_keyboard() -> InlineKeyboardMarkup:
    return _build("type", TYPE_OPTIONS)


def rooms_keyboard() -> InlineKeyboardMarkup:
    return _build("rooms", ROOMS_OPTIONS)


def renovation_keyboard() -> InlineKeyboardMarkup:
    return _build("renovation", RENOVATION_OPTIONS)


def wishes_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="Пропустить", callback_data="wishes:skip"))
    return builder.as_markup()


def result_keyboard() -> InlineKeyboardMarkup:
    return _build("result", RESULT_OPTIONS)


def retry_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="Повторить", callback_data="retry:study_area"))
    return builder.as_markup()
