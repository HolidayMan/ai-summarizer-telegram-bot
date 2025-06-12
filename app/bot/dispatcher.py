import aiogram

from app.bot.middlewares.auth import AuthMiddleware
from app.bot.routes.start import router as start_router

dispatcher = aiogram.Dispatcher()

dispatcher.message.middleware(AuthMiddleware())
dispatcher.include_router(start_router)
