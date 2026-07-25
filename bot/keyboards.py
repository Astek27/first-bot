from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder

START_BUTTON_TEXT = "🏠 Начать"

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


def _build(prefix: str, options: list[tuple[str, str]], per_row: int = 2) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for label, value in options:
        builder.add(InlineKeyboardButton(text=label, callback_data=f"{prefix}:{value}"))
    builder.adjust(per_row)
    return builder.as_markup()


def type_keyboard() -> InlineKeyboardMarkup:
    return _build("type", TYPE_OPTIONS)


def rooms_keyboard() -> InlineKeyboardMarkup:
    return _build("rooms", ROOMS_OPTIONS)


def renovation_keyboard() -> InlineKeyboardMarkup:
    return _build("renovation", RENOVATION_OPTIONS, per_row=1)


def wishes_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="Пропустить", callback_data="wishes:skip"))
    return builder.as_markup()


def result_keyboard() -> InlineKeyboardMarkup:
    return _build("result", RESULT_OPTIONS, per_row=1)


def retry_keyboard(callback_data: str = "retry:study_area") -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.add(InlineKeyboardButton(text="Повторить", callback_data=callback_data))
    return builder.as_markup()


def start_reply_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=START_BUTTON_TEXT)]],
        resize_keyboard=True,
    )
