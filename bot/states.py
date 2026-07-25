from aiogram.fsm.state import State, StatesGroup


class ListingForm(StatesGroup):
    waiting_link = State()
    waiting_type = State()
    waiting_rooms = State()
    waiting_area = State()
    waiting_floor = State()
    waiting_renovation = State()
    waiting_wishes = State()
    generating = State()
    result = State()
