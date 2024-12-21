from logic import PaymentCreator, PaymentLoader

from models import User, Payment
from telegram import Config


class PaymentService:
    client_id: str
    client_secret: str


    def __init__(
            self,
            payment_creator: PaymentCreator,
            payment_loader: PaymentLoader,
        ):
        self.payment_creator = payment_creator
        self.payment_loader = payment_loader


    async def create_like_payment(self, user: User) -> Payment:
        return await self.payment_creator.create_payment(target="likes", sum=2, user=user)

    async def create_message_payment(self, user: User) -> Payment:
        return await self.payment_creator.create_payment(target="messages", sum=2, user=user)

    async def is_payment_successful(self, payment_label: str) -> bool:
        return await self.payment_loader.is_successful(payment_label)
