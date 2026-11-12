# SMS: Limitar el contenido a 160 caracteres, registrar el número y la fecha de envío.
import asyncio
import re

from app.channels.base import (
    DeliveryResult,
    INotificationChannel,
    NotificationValidationError,
)
from app.models import Notification

SMS_REGEX_PHONE = re.compile(r"^\+\d{8,15}$")


class SmsChannel(INotificationChannel):
    name = "sms"

    def validate(self, notification: Notification) -> None:
        if not SMS_REGEX_PHONE.match(notification.recipient):
            raise NotificationValidationError(
                "recipient must be a phone number in E.164 format, e.g. +5491112345678"
            )
        if len(notification.content) > 160:
            raise NotificationValidationError("notification msg is limited to 160")

    async def send(self, notification: Notification) -> DeliveryResult:
        await asyncio.sleep(0.01)

        return DeliveryResult(
            status="sent",
            details={
                "recipient": notification.recipient,
                "length": len(notification.content),
            },
            error=None,  # result.error
        )
