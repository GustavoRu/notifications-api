from app.channels.sms import SmsChannel
from app.channels.email import EmailChannel
from app.channels.push import PushChannel
from app.channels.base import INotificationChannel, UnknownChannelError
    

# Agregar un método/canal = crear su clase y sumarla a esta lista. El service no cambia.
_CHANNELS: dict[str, INotificationChannel] = {m.name: m for m in [SmsChannel(), EmailChannel(), PushChannel()]}

def get_channel_notification(name: str) -> INotificationChannel:
    try:
        return _CHANNELS[name]
    except KeyError:
        raise UnknownChannelError(f"unknown notification channel: {name}") from None