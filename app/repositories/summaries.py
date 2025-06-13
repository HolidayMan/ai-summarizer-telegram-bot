from __future__ import annotations

from datetime import datetime

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.models import Summary


class SummariesRepository:
    async def save_summary(
        self,
        chat_id: int,
        content: str,
        since: datetime,
        until: datetime,
        session: AsyncSession,
    ) -> Summary:
        summary = Summary(
            chat_id=chat_id,
            summary_content=content,
            messages_since_time=since,
            messages_until_time=until,
            generated_at=datetime.utcnow(),
        )
        session.add(summary)
        await session.flush()
        return summary
