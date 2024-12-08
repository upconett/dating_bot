from telegram import BaseMiddleware, AIOgramMessage, TelegramObject
from typing import *
import asyncio


class MediaGroupMiddleware(BaseMiddleware):
    media_group_data: dict = {}

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        message: AIOgramMessage,
        data: Dict[str, Any]
    ) -> Any:
        if not message.media_group_id:
            data['media_group'] = None
            return await handler(message, data)
        try:
            self.media_group_data[message.media_group_id].append(message)
        except KeyError:
            self.media_group_data[message.media_group_id] = [message]
            await asyncio.sleep(0.01)

            data['_is_last'] = True
            data['media_group'] = self.media_group_data[message.media_group_id]

            result = await handler(message, data)

            if message.media_group_id and data.get("_is_last"):
                del self.media_group_data[message.media_group_id]
                del data['_is_last']

            return result