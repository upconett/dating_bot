from abc import ABC, abstractmethod

from models import Payment


class PaymentLoader(ABC):

    @abstractmethod
    async def is_successful(self, payment_label: str) -> bool:
        ...
