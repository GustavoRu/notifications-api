# Email: validate the recipient format, render a template and record the delivery.
import asyncio
import html
from string import Template

from email_validator import EmailNotValidError, validate_email

from app.channels.base import (
    DeliveryResult,
    INotificationChannel,
    NotificationValidationError,
)
from app.models import Notification

EMAIL_TEMPLATE = Template("""\
    <html>
    <body style="font-family: Arial, sans-serif; color: #333333; line-height: 1.6;">
        <h2 style="color: #2C3E50;">¡Hola!</h2>
        <div style="background-color: #F8F9FA; padding: 15px; border-left: 4px solid #3498DB; margin: 20px 0;">
        <p style="margin: 0;"><strong>$title</strong></p>
        <p>$content</p>
        </div>
        <p>Saludos cordiales,<br><strong>El equipo de Soporte</strong></p>
    </body>
    </html>
    """)


class EmailChannel(INotificationChannel):
    """Email: validate the recipient format, render a template and record the delivery."""

    name = "email"

    def validate(self, notification: Notification) -> None:
        try:
            validate_email(notification.recipient, check_deliverability=False)
        except EmailNotValidError as e:
            raise NotificationValidationError(str(e)) from None

    async def send(self, notification: Notification) -> DeliveryResult:
        email = self._render(notification)
        await asyncio.sleep(
            0.01
        )  # simulates the provider call without blocking the event loop

        if notification.recipient.startswith(
            "fail@"
        ):  # simulated failure, to test the "failed" status
            return DeliveryResult(
                status="failed",
                details=email,
                error="SMTP provider rejected the message",
            )
        return DeliveryResult(status="sent", details=email)

    def _render(self, notification: Notification) -> dict[str, str]:
        """Build what would be sent to the provider. User content is escaped to prevent HTML injection."""
        body = EMAIL_TEMPLATE.substitute(
            title=html.escape(notification.title),
            content=html.escape(notification.content),
        )
        return {
            "to": notification.recipient,
            "subject": f"Notificación - {notification.title}",
            "html": body,
        }
