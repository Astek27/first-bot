from aiogram import F, Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot.handlers.generate import run_generation
from bot.keyboards import (
    RENOVATION_OPTIONS,
    ROOMS_OPTIONS,
    TYPE_OPTIONS,
    renovation_keyboard,
    rooms_keyboard,
    wishes_keyboard,
)
from bot.states import ListingForm

router = Router()

TYPE_LABELS = dict(((value, label) for label, value in TYPE_OPTIONS))
ROOMS_LABELS = dict(((value, label) for label, value in ROOMS_OPTIONS))
RENOVATION_LABELS = dict(((value, label) for label, value in RENOVATION_OPTIONS))


@router.callback_query(StateFilter(ListingForm.waiting_type), F.data.startswith("type:"))
async def on_type(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    value = callback.data.split(":", 1)[1]
    await state.update_data(property_type=TYPE_LABELS[value])
    await state.set_state(ListingForm.waiting_rooms)
    await callback.message.answer("Сколько комнат?", reply_markup=rooms_keyboard())


@router.callback_query(StateFilter(ListingForm.waiting_rooms), F.data.startswith("rooms:"))
async def on_rooms(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    value = callback.data.split(":", 1)[1]
    await state.update_data(rooms=ROOMS_LABELS[value])
    await state.set_state(ListingForm.waiting_area)
    await callback.message.answer("Какая площадь, м²?")


@router.message(StateFilter(ListingForm.waiting_area), F.text)
async def on_area(message: Message, state: FSMContext) -> None:
    try:
        area = float(message.text.replace(",", "."))
    except ValueError:
        await message.answer("Введите площадь числом, например 54.5")
        return
    await state.update_data(area=f"{area:g}")
    await state.set_state(ListingForm.waiting_floor)
    await message.answer("Этаж / этажность дома? Например: 5/9")


@router.message(StateFilter(ListingForm.waiting_floor), F.text)
async def on_floor(message: Message, state: FSMContext) -> None:
    await state.update_data(floor=message.text)
    await state.set_state(ListingForm.waiting_renovation)
    await message.answer("Какой ремонт?", reply_markup=renovation_keyboard())


@router.callback_query(StateFilter(ListingForm.waiting_renovation), F.data.startswith("renovation:"))
async def on_renovation(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    value = callback.data.split(":", 1)[1]
    await state.update_data(renovation=RENOVATION_LABELS[value])
    await state.set_state(ListingForm.waiting_wishes)
    await callback.message.answer(
        "Есть пожелания к тексту объявления? Напишите одной строкой или пропустите.",
        reply_markup=wishes_keyboard(),
    )


@router.message(StateFilter(ListingForm.waiting_wishes), F.text)
async def on_wishes_text(message: Message, state: FSMContext) -> None:
    await state.update_data(wishes=message.text)
    await run_generation(message, state)


@router.callback_query(StateFilter(ListingForm.waiting_wishes), F.data == "wishes:skip")
async def on_wishes_skip(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    await state.update_data(wishes=None)
    await run_generation(callback.message, state)
