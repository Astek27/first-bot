from aiogram import F, Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot.config import Settings
from bot.keyboards import START_BUTTON_TEXT, retry_keyboard, start_reply_keyboard, type_keyboard
from bot.services.errors import ExternalServiceError
from bot.services.geocoder import resolve_address
from bot.services.maps_link import resolve_link
from bot.services.poi import find_poi
from bot.states import ListingForm

router = Router()

INTRO_TEXT = (
    "👋 Я помогу быстро составить текст объявления о продаже квартиры или дома в Москве.\n\n"
    "Пришлите ссылку на Яндекс.Карты с адресом объекта — я изучу район (метро, школы, "
    "детские сады поблизости), задам несколько вопросов о квартире и сгенерирую готовый "
    "текст объявления."
)


@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext) -> None:
    await start_flow(message, state)


@router.message(F.text == START_BUTTON_TEXT)
async def on_start_button(message: Message, state: FSMContext) -> None:
    await start_flow(message, state)


async def start_flow(message: Message, state: FSMContext) -> None:
    await state.set_state(ListingForm.waiting_link)
    await message.answer(INTRO_TEXT, reply_markup=start_reply_keyboard())


@router.message(StateFilter(ListingForm.waiting_link), F.text)
async def on_link(message: Message, state: FSMContext, settings: Settings) -> None:
    await state.update_data(link=message.text)
    await study_area(message, state, message.text, settings)


@router.callback_query(F.data == "retry:study_area")
async def on_retry(callback: CallbackQuery, state: FSMContext, settings: Settings) -> None:
    await callback.answer()
    data = await state.get_data()
    if "link" not in data:
        await callback.message.answer("Анкета сброшена (бот перезапускался). Начнём заново.")
        await start_flow(callback.message, state)
        return
    await study_area(callback.message, state, data["link"], settings)


async def study_area(message: Message, state: FSMContext, url: str, settings: Settings) -> None:
    await message.answer("Изучаю район... 🔍")
    try:
        coords = await resolve_link(url)
        address_info = await resolve_address(coords, settings.yandex_geocoder_api_key)
        if address_info.city != "Москва":
            await message.answer("Бот пока работает только по Москве.")
            return
        poi = await find_poi(coords)
    except ExternalServiceError:
        await message.answer(
            "Не получилось изучить район, попробуйте ещё раз.",
            reply_markup=retry_keyboard(),
        )
        return

    await state.update_data(address=address_info.address, poi=poi)
    await state.set_state(ListingForm.waiting_type)
    await message.answer("Какой тип объекта?", reply_markup=type_keyboard())
