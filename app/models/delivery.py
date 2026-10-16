from __future__ import annotations
from datetime import UTC, datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text, Column
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.sql import func

from app.database import Base


class Delivery(Base):
    __tablename__ = "deliveries"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    status: Mapped[str] = mapped_column(String(10), unique=False, nullable=False) #sent o failed
    details: Mapped[dict] = mapped_column(JSONB, unique=False, nullable=False)
    error: Mapped[str | None] = mapped_column(unique=False, nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    notification_id: Mapped[int] = mapped_column(ForeignKey("notifications.id"), index=True)

