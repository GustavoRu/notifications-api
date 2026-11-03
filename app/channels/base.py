from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Literal
from app.models import Notification

@dataclass
class DeliveryResult:
    """Lo que devuelve una estrategia. El service lo guarda; la estrategia no toca la base."""
    status: Literal["sent", "failed"]
    details: dict[str, Any] = field(default_factory=dict)
    error: str | None = None


class UnknownChannelError(Exception):
    pass


class NotificationValidationError(Exception):
    pass


class INotificationChannel(ABC):
    name: str  # la clave con la que el cliente elige el método

    @abstractmethod
    def validate(self, notification: Notification) -> None:
        """Lanza NotificationValidationError si la notificacion no cumple las reglas de este método."""

    @abstractmethod
    async def send(self, notification: Notification) -> DeliveryResult:
        """Ejecuta los pasos propios del método y devuelve el resultado."""