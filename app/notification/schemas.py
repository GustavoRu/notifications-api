from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

class NotificationBase(BaseModel):
    status: str = Field(min_length=1 ,max_length=10)
    title: str = Field(min_length=1 ,max_length=60)
    content: str = Field(min_length=1 ,max_length=250)
    channel: str = Field(min_length=1 ,max_length=10)
    recipient: str = Field(min_length=1 ,max_length=250)
    user: str = Field(min_length=1 ,max_length=10)

class NotificationBase(NotificationBase):
    id: int
    model_config = ConfigDict(from_attributes=True)
    created_at: datetime
