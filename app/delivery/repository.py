from abc import ABC, abstractmethod

from sqlalchemy.ext.asyncio import AsyncSession

from app.models import Delivery


class IDeliveryRepository(ABC):
    """Data access for delivery. Never commits: the service owns the transaction."""

    @abstractmethod
    async def add(self, delivery: Delivery) -> Delivery: ...


class DeliveryRepository(IDeliveryRepository):
    def __init__(self, session: AsyncSession):
        self._session = session

    async def add(self, delivery: Delivery) -> Delivery:
        self._session.add(delivery)
        await (
            self._session.flush()
        )  # sends the INSERT inside the open transaction: id is now set
        return delivery
