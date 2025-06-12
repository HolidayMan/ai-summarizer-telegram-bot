from app.bot.bot import BOT
from app.bot.dispatcher import dispatcher
import asyncio

async def main():
    await dispatcher.start_polling(BOT)

if __name__ == "__main__":
    asyncio.run(main())

