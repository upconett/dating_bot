from typing import List

from telegram import Config
from telegram import AIOgramBot, AIOgramMessage
from telegram import InputMediaPhoto, InputMediaVideo

from telegram.assets import messages, keyboards

from logic import CardLoader
from models import User, Card


class NotificationManager():
    bot: AIOgramBot
    card_loader: CardLoader
    admins: List[str]

    def __init__(
            self,
            bot: AIOgramBot,
            card_loader: CardLoader,
            config: Config
        ):
        self.bot = bot
        self.card_loader = card_loader
        self.admins = config.admins


    async def send_like(self, sender: User, receiver: User):
        card = await self.card_loader.get_by_id(sender.id)
        first_message = await self.bot.send_message(
            chat_id=receiver.tg_id,
            text=messages.YOU_BEEN_LIKED
        )
        await self._send_card(
            receiver=receiver,
            card=card,
            keyboard=keyboards.response_card(sender.tg_id),
            reply_to_message=first_message.message_id
        )

    
    async def send_response_like(self, sender: User, receiver: User):
        card = await self.card_loader.get_by_id(sender.id)
        first_message = await self._send_card(
            receiver=receiver,
            card=card
        )
        await self.bot.send_message(
            chat_id=receiver.tg_id,
            text=messages.response_like(sender, card),
            reply_to_message_id=first_message.message_id,
            parse_mode="HTML",
        )


    async def send_message(self, sender: User, receiver: User, message: str):
        card = await self.card_loader.get_by_id(sender.id)
        first_message = await self.bot.send_message(
            chat_id=receiver.tg_id,
            text=messages.received_message(message)
        )
        await self._send_card(
            receiver=receiver,
            card=card,
            keyboard=keyboards.response_card(sender.tg_id),
            reply_to_message=first_message.message_id
        )
    

    async def log_like_payment(self, user: User):
        for admin_id in self.admins:
            await self.bot.send_message(
                chat_id=admin_id,
                text=messages.like_payment_log(user)
            )

    async def log_message_payment(self, user: User):
        for admin_id in self.admins:
            await self.bot.send_message(
                chat_id=admin_id,
                text=messages.message_payment_log(user)
            )
        

    async def _send_card(self, receiver: User, card: Card, keyboard = None, reply_to_message: int = None):
        if len(card.media) == 0:
            return await self._send_card_without_media(receiver, card, keyboard, reply_to_message)
        else:
            return await self._send_card_with_single_media(receiver, card, keyboard, reply_to_message)

    
    async def _send_card_without_media(self, receiver: User, card: Card, keyboard = None, reply_to_message: int = None) -> AIOgramMessage:
        return await self.bot.send_message(
            chat_id=receiver.tg_id,
            text=messages.card_info(card),
            reply_markup=keyboard,
            reply_to_message_id=reply_to_message,
        )

    async def _send_card_with_single_media(self, receiver: User, card: Card, keyboard = None, reply_to_message: int = None) -> AIOgramMessage:
        media = card.media[0]
        match(media.type):
            case "photo":
                return await self.bot.send_photo(
                    chat_id=receiver.tg_id,
                    caption=messages.card_info(card),
                    photo=media.file_id,
                    reply_markup=keyboard,
                    reply_to_message_id=reply_to_message,
                )
            case "video":
                return await self.bot.send_video(
                    chat_id=receiver.tg_id,
                    caption=messages.card_info(card),
                    video=media.file_id,
                    reply_markup=keyboard,
                    reply_to_message_id=reply_to_message,
                )
            case _:
                return None


    # Redundant, because can not add reply_markup to media_group :(
    async def _send_card_with_media_group(self, message: AIOgramMessage, card: Card) -> AIOgramMessage:
        media_group: List[InputMediaPhoto|InputMediaVideo] = []
        for m in card.media:
            if m.type == "photo": media_group.append(InputMediaPhoto(media=m.file_id))
            if m.type == "video": media_group.append(InputMediaVideo(media=m.file_id))
        media_group[0].caption = messages.card_info(card)
        return await message.answer_media_group(media_group)

