# Validar el token de dispositivo, formatear el payload y registrar el estado del envío.
import re
import asyncio
from app.channels.base import (
    INotificationChannel,
    DeliveryResult,
    NotificationValidationError,
)
from app.models import Notification

PUSH_REGEX_PHONE = re.compile(r"^[a-zA-Z0-9_\-:]{20,255}$")


class PushChannel(INotificationChannel):
    """Validar el token de dispositivo, formatear el payload y registrar el estado del envío"""

    name = "push"

    def validate(self, notification: Notification) -> None:
        if not PUSH_REGEX_PHONE.match(notification.recipient):
            raise NotificationValidationError(
                "recipient must be a device token: 20-255 chars (letters, digits, _ - :)"
            )

    async def send(self, notification: Notification) -> DeliveryResult:
        await asyncio.sleep(0.01)

        token = notification.recipient
        payload = {
            "to": token,
            "notification": {"title": notification.title, "body": notification.content},
            "data": {"notification_id": notification.id},
        }

        if notification.recipient.startswith(
            "fail-"
        ):  # simulated failure, to test the "failed" status
            return DeliveryResult(
                status="failed",
                details={
                    "recipient": notification.recipient,
                    "payload": payload,
                },
                error="push provider rejected the notificacion",
            )

        return DeliveryResult(
            status="sent",
            details={
                "recipient": notification.recipient,
                "payload": payload,
            },
            error=None,  # result.error
        )
