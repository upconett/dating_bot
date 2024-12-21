import time                             # TODO: Use time to get seconds since epoch for unique labeling
from models import User, Payment
from telegram import Config

class PaymentService:
    client_id: str
    client_secret: str


    def __init__(
            self,
            config: Config
        ):
        self.client_id = config.client_id
        self.client_secret = config.client_secret


    async def create_like_payment(self, user: User) -> Payment:
        ...

    async def create_message_payment(self, user: User) -> Payment:
        ...

    async def is_payment_successful(self, payment_label: str) -> bool:
        ...
