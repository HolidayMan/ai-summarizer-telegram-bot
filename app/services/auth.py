from app.external_services.external_services import ExternalServices
from app.models.models import User
from app.repositories import Repositories


class AuthService:
    async def get_or_create_telegram_user(self, telegram_id: int,
                                          username: str | None = None,
                                          first_name: str | None = None,
                                          last_name: str | None = None
                                          ) -> User:
        async with ExternalServices.database.session() as session:
            if user := await Repositories.users.get_user_by_telegram_id(
                user_id=telegram_id,
                session=session
            ):
                return user
            user = await Repositories.users.create_user(
                user_id=telegram_id,
                username=username,
                first_name=first_name,
                last_name=last_name,
                session=session
            )
            await session.commit()
            return user
