from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError
from app.models.models import User
from datetime import datetime


class UserRepository:
    async def get_user_by_telegram_id(self, user_id: int, session: AsyncSession) -> User | None:
        query = select(User).where(User.id == user_id)
        result = await session.execute(query)
        return result.scalars().first()

    async def create_user(self, session: AsyncSession, user_id: int,
                          username: str | None = None,
                          first_name: str | None = None,
                          last_name: str | None = None) -> User:
        new_user = User(
            id=user_id,
            username=username,
            first_name=first_name,
            last_name=last_name,
            bot_interaction_created_at=datetime.utcnow()
        )
        session.add(new_user)
        try:
            await session.commit()
            return new_user
        except IntegrityError:
            await session.rollback()
            raise ValueError("User with this Telegram ID already exists.")
