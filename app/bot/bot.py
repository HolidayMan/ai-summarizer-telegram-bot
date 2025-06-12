import aiogram
from aiogram.client.default import DefaultBotProperties

from app.settings import get_settings
from app.external_services.external_services import ExternalServices
from app.bot.dispatcher import dispatcher

config = get_settings()
BOT_TOKEN = config.BOT_TOKEN

bot_properties = DefaultBotProperties(
    parse_mode=aiogram.enums.ParseMode.HTML,
)

BOT = aiogram.Bot(token=BOT_TOKEN, default=bot_properties)
