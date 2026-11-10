import pytest
from app.channels.sms import SmsChannel
from app.channels.email import EmailChannel
from app.channels.push import PushChannel
from app.channels.registry import get_channel_notification

from app.channels.base import NotificationValidationError, UnknownChannelError
from app.models import Notification

pytestmark = pytest.mark.anyio


def make_notification(**overrides) -> Notification:
    data = {
        "title": "Hola",
        "content": "Tu vuelo sale 10:30",
        "channel": "sms",
        "recipient": "+5491112345678",
        "status": "pending",
        "user_id": 1,
    }
    return Notification(**(data | overrides))


# SMS	El mensaje de 160 caracteres pasa y el de 161 rebota	pytest.raises(NotificationValidationError)
def test_sms_accepts_160_chars():
    notification = make_notification(content="x" * 160)
    result = SmsChannel().validate(notification)
    assert result is None


def test_sms_rejects_161_chars():
    notification = make_notification(content="x" * 161)
    with pytest.raises(NotificationValidationError):
        SmsChannel().validate(notification)


# SMS	Teléfonos inválidos ("hola", "12345", sin +)	Un solo test con @pytest.mark.parametrize
@pytest.mark.parametrize(
    "recipient",
    ["hola", "12345", "5491112345678", "------------", "+54 9 11 1234-5678"],
)
def test_sms_rejects_invalid_phone(recipient):
    notification = make_notification(recipient=recipient)
    with pytest.raises(NotificationValidationError):
        SmsChannel().validate(notification)


# SMS	send devuelve sent y el número en details	result = await channel.send(n) y assert sobre result
async def test_sms_send_records_phone_and_length():
    notification = make_notification()
    result = await SmsChannel().send(notification)
    assert result.status == "sent"
    assert "recipient" in result.details
    assert result.error is None
    assert result.details == {
        "recipient": notification.recipient,
        "length": len(notification.content),
    }


# Email con email valido
def test_email_valid_recipient():
    notification = make_notification(
        channel="email", content="xxxxxx", recipient="test@test.com"
    )
    result = EmailChannel().validate(notification)
    assert result is None


# Email con email invalido
@pytest.mark.parametrize(
    "recipient", ["hola", "mimail", "test@test", "------------", "test.com"]
)
def test_email_invalid_recipient(recipient):
    notification = make_notification(channel="email", recipient=recipient)
    with pytest.raises(NotificationValidationError):
        EmailChannel().validate(notification)


async def test_email_send_escapes_html_in_content():
    malicious = '<a href="http://phishing.example">Click aquí</a>'
    notification = make_notification(
        channel="email", recipient="test@test.com", content=malicious
    )

    result = await EmailChannel().send(notification)
    html = result.details["html"]

    assert malicious not in html
    assert "&lt;a href=&quot;http://phishing.example&quot;&gt;" in html


# push
def test_push_valid_recipient():
    notification = make_notification(
        channel="push",
        recipient="f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8:APA91bH_XYZ1234567890abcdefghijklmnopqrstuvwxyz_ABCDEFGHIJKLMNOPQRSTUVWXYZ-0123456789abcdefghijklmnopqrstuvwxyz",
    )
    result = PushChannel().validate(notification)
    assert result is None


# push con token invalido
@pytest.mark.parametrize(
    "recipient", ["fail-token", "mi token", "tokens", "------------", "token.com"]
)
def test_push_invalid_recipient(recipient):
    notification = make_notification(channel="push", recipient=recipient)
    with pytest.raises(NotificationValidationError):
        PushChannel().validate(notification)

async def test_push_send_records_failure():
    notification = make_notification(channel="push", recipient="fail-device-token-123456")

    PushChannel().validate(notification)  # el token es válido: el fallo ocurre en el envío, no en la validación
    result = await PushChannel().send(notification)

    assert result.status == "failed"
    assert result.error is not None
    assert "payload" in result.details

async def test_push_send_payload_and_recipient():
    notification = make_notification(
        channel="push",
        recipient="f7a8b9c0d1e2f3a4b5c6d7e8f9a0b1c2d3e4f5a6b7c8d9e0f1a2b3c4d5e6f7a8:APA91bH_XYZ1234567890abcdefghijklmnopqrstuvwxyz_ABCDEFGHIJKLMNOPQRSTUVWXYZ-0123456789abcdefghijklmnopqrstuvwxyz",
    )
    result = await PushChannel().send(notification)
    assert result.status == "sent"
    assert "recipient" in result.details
    assert "payload" in result.details
    assert result.error is None
    assert result.details["payload"]["to"] == notification.recipient


# registry
def test_registry_rejects_unknown_channel():
    notification = make_notification(
        channel="fax",
    )
    with pytest.raises(UnknownChannelError):
        get_channel_notification(notification.channel)
