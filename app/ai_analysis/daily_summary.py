from __future__ import annotations

"""Scheduler task that generates daily summaries for chats at configured times."""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Sequence

from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest
from sched import scheduler
import time as time_mod

from app.external_services.external_services import ExternalServices
from app.repositories import Repositories
from app.settings import get_settings
from openai import AsyncOpenAI

logger = logging.getLogger(__name__)



class DailySummaryGenerator:
    MAX_TOKENS = 1500

    def __init__(self, bot: Bot):
        self._bot = bot
        self._cfg = get_settings()
        self.openai = AsyncOpenAI(api_key=self._cfg.OPENAI_API_KEY)

    async def _generate_summary_content(
        self, messages: Sequence[str], docs: Sequence[str]
    ) -> str:
        body = "\n".join(messages + docs)
        resp = await self.openai.chat.completions.create(
            model=self._cfg.OPENAI_MODEL,
            max_tokens=self.MAX_TOKENS,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a helpful assistant that writes daily chat digests. "
                        "Return concise plain-text summary (no markdown). Make it structured. "
                        "Don't forget to greet users in chat with a friendly 'Hello' or 'Hi'. "
                        "Introduce the message topic and highlight the main points. "
                    ),
                },
                {"role": "user", "content": body},
            ],
        )
        return resp.choices[0].message.content.strip()

    async def _collect_data(self, chat_id: int, now: datetime):
        since = now - timedelta(hours=24)
        since = since.replace(tzinfo=None)
        async with ExternalServices.database.session() as session:
            msgs = await Repositories.chats.get_messages_between(chat_id, since, now, session)
            docs = await Repositories.chats.get_documents_summaries_between(
                chat_id, since, now, session
            )
        messages_text = [m.message_text or "" for m in msgs if m.message_text]
        return messages_text, docs, since

    async def _save_and_send(
        self, chat_id: int, summary: str, since: datetime, until: datetime
    ) -> None:
        async with ExternalServices.database.session() as session:
            await Repositories.summaries.save_summary(
                chat_id, summary, since, until, session
            )
            await session.commit()

        try:
            await self._bot.send_message(chat_id, summary)
        except TelegramBadRequest as exc:
            logger.warning("Failed to send summary to %s: %s", chat_id, exc)

    async def run_once(self, now: datetime | None = None):
        now = now or datetime.now()
        # ensure naive datetime for DB comparisons
        if now.tzinfo is not None:
            now = now.replace(tzinfo=None)
        async with ExternalServices.database.session() as session:
            chat_ids = await Repositories.chats.get_chats_due_for_summary(now, session)
        print(now, chat_ids)

        for chat_id in chat_ids:
            msgs, docs, since = await self._collect_data(chat_id, now)
            if not msgs and not docs:
                continue
            summary = await self._generate_summary_content(msgs, docs)
            await self._save_and_send(chat_id, summary, since, now)


async def scheduled_runner():
    from app.bot.bot import BOT

    generator = DailySummaryGenerator(BOT)

    sched = scheduler(time_mod.time, time_mod.sleep)

    async def tick():
        while True:
            now = datetime.now()
            await generator.run_once(now)
            await asyncio.sleep(60)  # run every minute

    asyncio.create_task(tick())

    sched.run()
