from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models import Notification
from app.notification.schemas import NotificationCreate, NotificationRead
from app.database import get_db
from app.auth.dependencies import CurrentUser
from app.config import settings

router = APIRouter(prefix="/notifications", tags=["notifications"])


@router.post(
    "",
    status_code=status.HTTP_201_CREATED,
    response_model=NotificationRead,
)
async def create_notification(
    notification: NotificationCreate,
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: CurrentUser,
):
    new_notification = Notification(
        **notification.model_dump(), user_id=current_user.id, status="pending"
    )

    db.add(new_notification)
    await db.commit()
    await db.refresh(new_notification)
    return new_notification


@router.get("", response_model=list[NotificationRead])
async def get_notifications(
    db: Annotated[AsyncSession, Depends(get_db)],
    current_user: CurrentUser,
    page: Annotated[int, Query(ge=1)] = 1,
    per_page: Annotated[int, Query(ge=1, le=100)] = 10,
):
    result = await db.execute(
        select(Notification)
        .where(Notification.user_id == current_user.id)
        .order_by(desc(Notification.created_at))
        .offset((page - 1) * per_page)
        .limit(per_page)
    )
    return result.scalars().all()
