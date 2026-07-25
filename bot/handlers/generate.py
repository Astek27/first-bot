from aiogram import F, Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from bot.config import Settings
from bot.handlers.link import start_flow
from bot.keyboards import result_keyboard, retry_keyboard
from bot.services.errors import ExternalServiceError
from bot.services.llm import ListingInput, generate_listing
from bot.states import ListingForm

router = Router()


async def run_generation(message: Message, state: FSMContext, settings: Settings) -> None:
    await state.set_state(ListingForm.generating)
    await message.answer("Генерирую текст объявления...")

    data = await state.get_data()
    listing_input = ListingInput(
        address=data["address"],
        poi=data["poi"],
        property_type=data["property_type"],
        rooms=data["rooms"],
        area=data["area"],
        floor=data["floor"],
        renovation=data["renovation"],
        wishes=data.get("wishes"),
    )
    try:
        text = await generate_listing(listing_input, settings.gigachat_api_key)
    except ExternalServiceError:
        await message.answer(
            "Сервис генерации временно недоступен (лимит GigaChat исчерпан или сбой). "
            "Попробуйте позже.",
            reply_markup=retry_keyboard("retry:generate"),
        )
        return

    await state.set_state(ListingForm.result)
    await message.answer(text, reply_markup=result_keyboard())


@router.callback_query(F.data == "retry:generate")
async def on_retry_generate(callback: CallbackQuery, state: FSMContext, settings: Settings) -> None:
    await callback.answer()
    await run_generation(callback.message, state, settings)


@router.callback_query(StateFilter(ListingForm.result), F.data == "result:regenerate")
async def on_regenerate(callback: CallbackQuery, state: FSMContext, settings: Settings) -> None:
    await callback.answer()
    await run_generation(callback.message, state, settings)


@router.callback_query(StateFilter(ListingForm.result), F.data == "result:restart")
async def on_restart(callback: CallbackQuery, state: FSMContext) -> None:
    await callback.answer()
    await state.clear()
    await start_flow(callback.message, state)
