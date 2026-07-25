from aiogram import F, Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot.keyboards import retry_keyboard, type_keyboard
from bot.services.errors import ExternalServiceError
from bot.services.geocoder import resolve_address
from bot.services.maps_link import resolve_link
from bot.services.poi import find_poi
from bot.states import ListingForm

router = Router()


@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext) -> None:
    await state.set_state(ListingForm.waiting_link)
    await message.answer("Пришлите ссылку на Яндекс.Карты с адресом квартиры.")


@router.message(StateFilter(ListingForm.waiting_link), F.text)
async def on_link(message: Message, state: FSMContext) -> None:
    await state.update_data(link=message.text)
    await study_area(message, state, message.text)


@router.callback_query(F.data == "retry:study_area")
async def on_retry(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    data = await state.get_data()
    await study_area(callback.message, state, data["link"])


async def study_area(message: Message, state: FSMContext, url: str) -> None:
    await message.answer("Изучаю район... 🔍")
    try:
        coords = await resolve_link(url)
        address_info = await resolve_address(coords)
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
