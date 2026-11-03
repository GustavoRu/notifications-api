from typing import Annotated

from fastapi import APIRouter, HTTPException, status, Query

from app.notification.schemas import (
    NotificationCreate,
    NotificationRead,
    NotificationUpdate,
)
from app.auth.dependencies import CurrentUser
from app.notification.service import NotificationServiceDep, NotificationNotFoundError
from app.channels.base import UnknownChannelError, NotificationValidationError

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=NotificationRead,
)
async def create_notification(
    notification: NotificationCreate,
    current_user: CurrentUser,
    service: NotificationServiceDep,
):
    try:
        return await service.create(current_user.id, notification)
    except (UnknownChannelError, NotificationValidationError) as e:
        raise HTTPException(status_code=422, detail=str(e)) from None


@router.get("", response_model=list[NotificationRead])
async def get_notifications(
    current_user: CurrentUser,
    service: NotificationServiceDep,
    page: Annotated[int, Query(ge=1)] = 1,
    per_page: Annotated[int, Query(ge=1, le=100)] = 10,
):
    return await service.list(current_user.id, page, per_page)


@router.patch("/{notification_id}", response_model=NotificationRead)
async def update_notification(
    notification_id: int,
    notification_update: NotificationUpdate,
    current_user: CurrentUser,
    service: NotificationServiceDep,
):
    try:
        return await service.update(
            current_user.id, notification_id, notification_update
        )
    except NotificationNotFoundError:
        raise HTTPException(status_code=404, detail="Notification not found") from None


@router.delete("/{notification_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_notification(
    notification_id: int,
    current_user: CurrentUser,
    service: NotificationServiceDep,
):
    try:
        await service.delete(current_user.id, notification_id)
    except NotificationNotFoundError:
        raise HTTPException(status_code=404, detail="Notification not found") from None
