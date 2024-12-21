import asyncio
import concurrent.futures
from time import time

from yoomoney import Client as YooClient, Quickpay

from logic import PaymentCreator
from telegram import Config

from models import User, Payment


class ThreadedPaymentCreator(PaymentCreator):

    def __init__(
            self,
            yoomoney_client: YooClient,
            config: Config
        ):
        self.client = yoomoney_client
        self.info = self.client.account_info()
        self.redirect_url = config.redirect_url


    async def create_payment(self, target: str, sum: int, user: User) -> Payment:
        loop = asyncio.get_running_loop()
        with concurrent.futures.ThreadPoolExecutor() as pool:
            payment = await loop.run_in_executor(pool, self._sync_create_payment, target, sum, user)
        return payment


    def _sync_create_payment(self, target: str, sum: int, user: User) -> Payment:
        quickpay = Quickpay(
            receiver=self.info.account,
            quickpay_form="shop",
            targets=target,
            paymentType="SB",
            sum=sum,
            label=self._generate_label(user)
        )
        return Payment(
            id=-1,
            label=quickpay.label,
            base_url=quickpay.base_url,
            redirected_url=quickpay.redirected_url
        )

    
    def _generate_label(self, user: User) -> str:
        return f"{user.tg_id}:{int(round(time()*1000))}"
