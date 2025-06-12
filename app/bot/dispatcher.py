import aiogram

from app.bot.middlewares.auth import AuthMiddleware
from app.bot.routes.start import router as start_router
from app.bot.routes.set_time import router as set_time_router
from app.bot.routes.add_to_channel import router as add_to_channel_router

dispatcher = aiogram.Dispatcher()

dispatcher.message.middleware(AuthMiddleware())
dispatcher.include_router(start_router)
dispatcher.include_router(set_time_router)
dispatcher.include_router(add_to_channel_router)
