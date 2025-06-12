from datetime import datetime
from typing import Optional
from uuid import uuid4

from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
import sqlalchemy as sa


class ModelsBase(DeclarativeBase):
    __abstract__ = True

    id: Mapped[sa.UUID] = mapped_column(sa.UUID(as_uuid=True), primary_key=True, default=uuid4())

    created_at: Mapped[datetime] = mapped_column(sa.DateTime, nullable=False, default=sa.func.now())
    updated_at: Mapped[datetime] = mapped_column(sa.DateTime, server_default=sa.func.now(), onupdate=sa.func.now())
    deleted_at: Mapped[datetime | None] = mapped_column(sa.DateTime, nullable=True)

    def __repr__(self):
        return f"<{self.__class__.__name__}: #{self.id}>"