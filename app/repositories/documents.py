from __future__ import annotations

from datetime import datetime
from typing import Sequence

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.models import Document, AnalysisProcessingStatusEnum


class DocumentsRepository:
    async def get_unprocessed_documents(
        self, batch_size: int, session: AsyncSession
    ) -> Sequence[Document]:
        stmt = (
            select(Document)
            .where(Document.processing_status == AnalysisProcessingStatusEnum.NOT_STARTED.value)  # type: ignore[arg-type]
            .limit(batch_size)
        )
        result = await session.execute(stmt)
        return result.scalars().all()

    async def mark_pending(self, documents: Sequence[Document], session: AsyncSession) -> None:
        now = datetime.utcnow()
        stmt = select(Document).where(Document.id.in_([doc.id for doc in documents]))
        result = await session.execute(stmt)

        documents = result.scalars().all()

        for document in documents:
            document.processing_status = AnalysisProcessingStatusEnum.PENDING.value  # type: ignore[assignment]
            document.analysis_started_at = now
        await session.flush()

    async def save_summary(
        self, document: Document, summary: str, session: AsyncSession
    ) -> None:
        stmt = select(Document).where(Document.id == document.id)

        result = await session.execute(stmt)

        document = result.scalars().one_or_none()
        if not document:
            return

        document.analysis_content = summary
        document.processing_status = AnalysisProcessingStatusEnum.ANALYZED.value  # type: ignore[assignment]
        document.analysis_completed_at = datetime.utcnow()
        await session.flush()

    async def mark_error(self, document: Document, session: AsyncSession) -> None:
        document.processing_status = AnalysisProcessingStatusEnum.ERROR.value  # type: ignore[assignment]
        await session.flush()
