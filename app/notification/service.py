from typing import Annotated

from fastapi import Depends

from sqlalchemy.ext.asyncio import AsyncSession
from app.notification.repository import INotificationRepository, NotificationRepository
from app.models import Notification
from app.notification.schemas import NotificationCreate, NotificationUpdate
from app.database import get_db

class NotificationNotFoundError(Exception):
    """La notificacion no existe, está borrada o es de otro usuario."""

class NotificationService:
    def __init__(self, session: AsyncSession, notification_repository: INotificationRepository):
        self._session = session
        self._noti_repository = notification_repository

    async def create(self, user_id: int, noti_to_create: NotificationCreate) -> Notification:
        noti = Notification(**noti_to_create.model_dump(), user_id=user_id, status="pending")
        await self._noti_repository.add(noti)
        await self._session.commit()
        await self._session.refresh(noti)
        return noti    

    async def list(self, user_id: int, page: int, per_page: int) -> list[Notification]:
        return await self._noti_repository.list_for_user(user_id, limit=per_page, offset=(page - 1) * per_page)

    async def get(self, user_id: int, noti_id: int) -> Notification:
        result = await self._noti_repository.get_for_user(noti_id, user_id)
        if result is None:
            raise NotificationNotFoundError(noti_id)
        return result

    async def update(self, user_id: int, noti_id: int, noti_to_update: NotificationUpdate) -> Notification:
        result_noti = await self.get(user_id, noti_id)
        for field, value in noti_to_update.model_dump(exclude_unset=True).items():
            setattr(result_noti, field, value)
        await self._session.commit()
        await self._session.refresh(result_noti)
        return result_noti    

    async def delete(self, user_id: int, noti_id: int) -> None:
        result_noti = await self.get(user_id, noti_id)
        await self._noti_repository.delete(result_noti)
        await self._session.commit()


def get_notification_repository(db: Annotated[AsyncSession, Depends(get_db)]) -> INotificationRepository:
    return NotificationRepository(db)


def get_notification_service(
    db: Annotated[AsyncSession, Depends(get_db)],
    repo: Annotated[INotificationRepository, Depends(get_notification_repository)],
) -> NotificationService:
    return NotificationService(db, repo)


NotificationServiceDep = Annotated[NotificationService, Depends(get_notification_service)]      