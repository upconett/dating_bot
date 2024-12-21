import asyncio
import concurrent.futures
from yoomoney import Client as YooClient

from logic import PaymentLoader

from models import Payment


class ThreadedPaymentLoader(PaymentLoader):

    def __init__(self, yoomoney_client: YooClient):
        self.client = yoomoney_client
        self.info = self.client.account_info()


    async def is_successful(self, payment_label: str) -> bool:
        loop = asyncio.get_running_loop()
        with concurrent.futures.ThreadPoolExecutor() as pool:
            result = await loop.run_in_executor(pool, self._sync_is_successful, payment_label)
        return result
        
    def _sync_is_successful(self, payment_label: str) -> bool:
        history = self.client.operation_history(label=payment_label)
        if len(history.operations) == 0: return False
        if history.operations[0].status == "success": return True
        return False
