import pytest
from app.channels.sms import SmsChannel

from app.channels.base import (
    NotificationValidationError,
)
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
@pytest.mark.parametrize("recipient", ["hola", "12345", "5491112345678"])
async def test_sms_rejects_invalid_phone(recipient):
    notification = make_notification(recipient=recipient)
    with pytest.raises(NotificationValidationError):
        SmsChannel().validate(notification)

# SMS	send devuelve sent y el número en details	result = await channel.send(n) y assert sobre result
