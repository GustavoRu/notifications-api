# SMS: Limitar el contenido a 160 caracteres, registrar el número y la fecha de envío.
import re
import asyncio
from app.channels.base import (
    INotificationChannel,
    DeliveryResult,
    NotificationValidationError,
)
from app.models import Notification

SMS_REGEX_PHONE = re.compile(r'^(\+?\d{1,4}[-.\s]?)?(\(?\d{1,3}\)?[-.\s]?)?[\d.\s-]{7,12}$')


class SmsChannel(INotificationChannel):
    name = "sms"

    def validate(self, notification: Notification) -> None:
        if not SMS_REGEX_PHONE.match(notification.recipient):
            raise NotificationValidationError("notification recipient is invalid")
        if len(notification.content) > 160:
            raise NotificationValidationError("notification msg are limited to 160")

    async def send(self, notification: Notification) -> DeliveryResult:
        await asyncio.sleep(0.01)

        return DeliveryResult(
            status="sent",
            details={"recipient": notification.recipient, "lenght_msg": len(notification.content)},
            error=None,  # result.error
        )
