from abc import ABC, abstractmethod
from datetime import UTC, datetime

from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Notification


class INotificationRepository(ABC):
    """Data access for notifications. Never commits: the service owns the transaction."""

    @abstractmethod
    async def add(self, notification: Notification) -> Notification: ...

    @abstractmethod
    async def get_for_user(
        self, notification_id: int, user_id: int
    ) -> Notification | None: ...

    @abstractmethod
    async def list_for_user(
        self, user_id: int, limit: int, offset: int
    ) -> list[Notification]: ...

    @abstractmethod
    async def delete(self, notification: Notification) -> None: ...


class NotificationRepository(INotificationRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def add(self, notification: Notification) -> Notification:
        self._session.add(notification)
        await (
            self._session.flush()
        )  # sends the INSERT inside the open transaction: id is now set
        return notification

    async def get_for_user(
        self, notification_id: int, user_id: int
    ) -> Notification | None:
        result = await self._session.execute(
            select(Notification).where(
                Notification.id == notification_id,
                Notification.user_id == user_id,
                Notification.deleted_at.is_(None),
            )
        )
        return result.scalar_one_or_none()

    async def list_for_user(
        self, user_id: int, limit: int, offset: int
    ) -> list[Notification]:
        result = await self._session.execute(
            select(Notification)
            .where(
                Notification.user_id == user_id,
                Notification.deleted_at.is_(None),
            )
            .order_by(desc(Notification.created_at), desc(Notification.id))
            .offset(offset)
            .limit(limit)
        )
        return list(result.scalars().all())

    async def delete(self, notification: Notification) -> None:
        notification.deleted_at = datetime.now(
            UTC
        )  # soft delete: the row and its deliveries stay
        await self._session.flush()
