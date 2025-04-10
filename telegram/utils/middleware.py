from telegram import BaseMiddleware, AIOgramMessage, TelegramObject, AIOgramQuery
from typing import *
import asyncio

from services import UserService

from telegram.utils.for_banned import banned_handler


class DefaultMiddleware(BaseMiddleware):
    user_service: UserService

    def __init__(self, user_service: UserService):
        self.user_service = user_service
        super().__init__()

    async def __call__(
                self,
                handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
                event: AIOgramMessage | AIOgramQuery,
                data: Dict[str, Any]
        ) -> Any:
            if hasattr(event, "chat"):
                user = await self.user_service.get_by_chat(event.chat)
            else:
                user = await self.user_service.get_by_tg_id(event.from_user.id)
            data['user'] = user
            if user.banned:
                return await banned_handler(event, user)
            return await handler(event, data)


# Sorry for that middleware, I confess, I do not understand what's going on in it
# It just works, so I adore it
class MediaGroupMiddleware(BaseMiddleware):
    media_group_data: dict = {}
    user_service: UserService

    def __init__(self, user_service: UserService):
        self.user_service = user_service
        super().__init__()

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: AIOgramMessage | AIOgramQuery,
        data: Dict[str, Any]
    ) -> Any:
        if event.__class__ == AIOgramQuery:
            return await handler(event, data)
        message = event
        user = await self.user_service.get_by_chat(message.chat)
        data['user'] = user
        if user.banned:
            return await banned_handler(event, user)
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
