from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class NotificationBase(BaseModel):
    # status: str = Field(min_length=1 ,max_length=10)
    title: str = Field(min_length=1, max_length=60)
    content: str = Field(min_length=1, max_length=250)
    channel: str = Field(min_length=1, max_length=10)
    recipient: str = Field(min_length=1, max_length=250)
    # user: str = Field(min_length=1 ,max_length=10)


class NotificationCreate(NotificationBase):
    pass


class NotificationUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=60)
    content: str | None = Field(default=None, min_length=1, max_length=250)
    channel: str | None = Field(default=None, min_length=1, max_length=10)
    recipient: str | None = Field(default=None, min_length=1, max_length=250)

    @field_validator("title", "content", "channel", "recipient")
    @classmethod
    def reject_explicit_null(cls, value):
        if value is None:
            raise ValueError("cannot be null")
        return value


class NotificationRead(NotificationBase):
    id: int
    created_at: datetime
    status: str
    model_config = ConfigDict(from_attributes=True)
