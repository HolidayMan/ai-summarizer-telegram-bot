from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timezone

from app.ai_analysis.document_processor import DocumentProcessor
from app.ai_analysis.daily_summary import DailySummaryGenerator

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)


async def _document_loop(processor: DocumentProcessor):
    """Endless loop for processing documents."""
    await processor.run_forever()


async def _summary_loop(generator: DailySummaryGenerator):
    """Check once per minute which chats need a digest and send it."""
    while True:
        now = datetime.utcnow().replace(tzinfo=timezone.utc)
        await generator.run_once(now)
        await asyncio.sleep(60)


async def run() -> None:  # noqa: D401  # Same signature as other modules
    from app.bot.bot import BOT  # Deferred import to avoid circular deps

    processor = DocumentProcessor(BOT)
    generator = DailySummaryGenerator(BOT)

    await asyncio.gather(
        _document_loop(processor),
        _summary_loop(generator),
        return_exceptions=False,
    )


# for manual testing: `python -m app.ai_analysis.daemon`
if __name__ == "__main__":
    asyncio.run(run())
