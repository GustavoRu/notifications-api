import logging
from typing import Annotated

from fastapi import Depends

from sqlalchemy.ext.asyncio import AsyncSession
from app.notification.repository import INotificationRepository, NotificationRepository
from app.delivery.deliveryRepository import IDeliveryRepository, DeliveryRepository
from app.models import Notification, Delivery
from app.channels.base import DeliveryResult
from app.notification.schemas import NotificationCreate, NotificationUpdate
from app.database import get_db
from app.channels.registry import get_channel_notification

logger = logging.getLogger(__name__)

class NotificationNotFoundError(Exception):
    """La notificacion no existe, está borrada o es de otro usuario."""


class NotificationService:
    def __init__(
        self, session: AsyncSession, notification_repository: INotificationRepository, delivery_repository: IDeliveryRepository
    ):
        self._session = session
        self._noti_repository = notification_repository
        self._delivery_repository = delivery_repository
        
    async def create(
        self, user_id: int, noti_to_create: NotificationCreate
    ) -> Notification:
        """Validate with the channel rules, save as pending, send, and record the delivery.

        Everything runs in one transaction: invalid notifications are never saved,
        and a failed send is stored with status "failed" instead of raising.
        """
        # noti = Notification(**noti_to_create.model_dump(), user_id=user_id, status="pending")
        # await self._noti_repository.add(noti)
        # await self._session.commit()
        # await self._session.refresh(noti)
        # return noti
        strategy = get_channel_notification(
            noti_to_create.channel
        ) 
        noti = Notification(
            **noti_to_create.model_dump(), user_id=user_id, status="pending"
        ) 
        strategy.validate(noti)

        await self._noti_repository.add(
            noti
        )

        try:
            result = await strategy.send(noti)  
        except Exception as e:
            result = DeliveryResult(status="failed", error=str(e))
            logger.exception("Channel %s failed to send notification %s", strategy.name, noti.id)


        await self._delivery_repository.add(
            Delivery(
                notification_id=noti.id,
                status=result.status,
                details=result.details,
                error=result.error,
            )
        )
        noti.status = result.status
        await self._session.commit()
        await self._session.refresh(noti)
        return noti

    async def list(self, user_id: int, page: int, per_page: int) -> list[Notification]:
        return await self._noti_repository.list_for_user(
            user_id, limit=per_page, offset=(page - 1) * per_page
        )

    async def get(self, user_id: int, noti_id: int) -> Notification:
        result = await self._noti_repository.get_for_user(noti_id, user_id)
        if result is None:
            raise NotificationNotFoundError(noti_id)
        return result

    async def update(
        self, user_id: int, noti_id: int, noti_to_update: NotificationUpdate
    ) -> Notification:
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


def get_notification_repository(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> INotificationRepository:
    return NotificationRepository(db)

def get_delivery_repository(
    db: Annotated[AsyncSession, Depends(get_db)],
) -> IDeliveryRepository:
    return DeliveryRepository(db)

def get_notification_service(
    db: Annotated[AsyncSession, Depends(get_db)],
    repo: Annotated[INotificationRepository, Depends(get_notification_repository)],
    delivery_repo: Annotated[IDeliveryRepository, Depends(get_delivery_repository)]
) -> NotificationService:
    return NotificationService(db, repo, delivery_repo)


NotificationServiceDep = Annotated[
    NotificationService, Depends(get_notification_service)
]
