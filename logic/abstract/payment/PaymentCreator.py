from abc import ABC, abstractmethod

from models import User, Payment


class PaymentCreator(ABC):
    
    @abstractmethod
    async def create_payment(self, target: str, sum: int, user: User) -> Payment:
        ...
