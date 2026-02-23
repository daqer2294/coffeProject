from sqlalchemy.ext.asyncio import AsyncSession

from database.models import AdminMessage


class AdminMessageRepository:

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(
        self,
        admin_telegram_id: int,
        user_id: int,
        text: str,
        visit_id: int | None = None,
        status: str = "sent",
    ) -> AdminMessage:

        message = AdminMessage(
            admin_telegram_id=admin_telegram_id,
            user_id=user_id,
            visit_id=visit_id,
            text=text,
            status=status,
        )

        self.session.add(message)
        await self.session.commit()
        await self.session.refresh(message)

        return message