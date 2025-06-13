from __future__ import annotations

import fitz

import asyncio
import logging
from io import BytesIO
from typing import Sequence

import openai
from aiogram import Bot
from aiogram.exceptions import TelegramBadRequest

from app.external_services.external_services import ExternalServices
from app.models.models import Document
from app.repositories import Repositories
from app.settings import get_settings

logger = logging.getLogger(__name__)


class DocumentProcessor:
    BATCH_SIZE = 3
    SUMMARY_TOKEN_LIMIT = 200

    def __init__(self, bot: Bot):
        self._bot = bot
        self._cfg = get_settings()
        self.openai = openai.AsyncOpenAI(api_key=self._cfg.OPENAI_API_KEY)

    async def _download_document(self, telegram_file_id: str) -> str | None:
        try:
            file = await self._bot.get_file(telegram_file_id)
            bio = BytesIO()
            await self._bot.download_file(file.file_path, destination=bio)
            bio.seek(0)

            # Parse PDF
            with fitz.open(stream=bio.read(), filetype="pdf") as doc:
                text = ""
                for page in doc:
                    text += page.get_text()
            return text.strip()
        except TelegramBadRequest as exc:
            logger.warning("Failed to download file %s: %s", telegram_file_id, exc)
            return None
        except Exception as e:
            logger.warning("Failed to extract text from PDF: %s", e)
            return None

    async def _summarize(self, text: str) -> str:
        resp = await self.openai.chat.completions.create(
            model=self._cfg.OPENAI_MODEL,
            max_tokens=self.SUMMARY_TOKEN_LIMIT,
            messages=[
                {
                    "role": "system",
                    "content": (
                        "You are a helpful assistant that summarizes documents. "
                        "Return a concise summary (plain text, no markdown)."
                    ),
                },
                {
                    "role": "user",
                    "content": "Summarize the following document:",
                },
                {
                    "role": "user",
                    "content": text,
                },
            ],
        )
        return resp.choices[0].message.content.strip()

    async def _process_batch(self, docs: Sequence[Document]) -> None:
        async with ExternalServices.database.session() as session:
            # Mark as pending early to avoid duplicate processing
            await Repositories.documents.mark_pending(docs, session)
            await session.commit()

        for doc in docs:
            try:
                file_bytes = await self._download_document(doc.telegram_file_id)
                if file_bytes is None:
                    async with ExternalServices.database.session() as session:
                        await Repositories.documents.mark_error(doc, session)
                        await session.commit()
                    continue

                summary = await self._summarize(file_bytes)
                async with ExternalServices.database.session() as session:
                    await Repositories.documents.save_summary(doc, summary, session)
                    await session.commit()
            except Exception as exc:  # pylint: disable=broad-except
                logger.exception("Error processing document %s: %s", doc.id, exc)
                async with ExternalServices.database.session() as session:
                    await Repositories.documents.mark_error(doc, session)
                    await session.commit()

    async def run_once(self) -> None:
        async with ExternalServices.database.session() as session:
            docs = await Repositories.documents.get_unprocessed_documents(
                batch_size=self.BATCH_SIZE, session=session
            )

        if not docs:
            return

        await self._process_batch(docs)

    async def run_forever(self, poll_interval: float = 5.0):
        while True:
            await self.run_once()
            await asyncio.sleep(poll_interval)


async def run():  # entry for scripts
    from app.bot.bot import BOT  # local import to avoid circular deps

    processor = DocumentProcessor(BOT)
    await processor.run_forever()
