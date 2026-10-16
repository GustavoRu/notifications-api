from __future__ import annotations
from datetime import UTC, datetime

from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from sqlalchemy.sql import func

from app.database import Base

#from typing import TYPE_CHECKING

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True) # index=True
    username: Mapped[str] = mapped_column(String(50), unique=True, nullable=False) #unique=False, nullable=False
    email: Mapped[str] = mapped_column(String(120), unique=True, nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(250))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    notifications: Mapped[list[Notification]] = relationship()