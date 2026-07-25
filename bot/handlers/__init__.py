from aiogram import Router

from bot.handlers.generate import router as generate_router
from bot.handlers.link import router as link_router
from bot.handlers.property import router as property_router

router = Router()
router.include_router(link_router)
router.include_router(property_router)
router.include_router(generate_router)
