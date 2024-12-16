from typing import *
from models import Card
from telegram import (
    AIOgramMessage,
    InputMediaPhoto, InputMediaVideo,
    InlineKeyboard, ReplyKeyboard
)

from telegram.assets import messages


async def send_card(message: AIOgramMessage, card: Card, keyboard: InlineKeyboard | ReplyKeyboard) -> AIOgramMessage:
    if len(card.media) == 0:
        return await _send_card_without_media(message, card, keyboard)
    elif len(card.media) == 1:
        return await _send_card_with_single_media(message, card, keyboard)
    elif len(card.media) > 1:
        return await _send_card_with_media_group(message, card)


async def _send_card_without_media(message: AIOgramMessage, card: Card, keyboard: InlineKeyboard | ReplyKeyboard) -> AIOgramMessage:
    return await message.answer(
        text=messages.card_info(card),
        reply_markup=keyboard,
        parse_mode='HTML',
    )

async def _send_card_with_media_group(message: AIOgramMessage, card: Card) -> AIOgramMessage:
    media_group: List[InputMediaPhoto|InputMediaVideo] = []
    for m in card.media:
        if m.type == "photo": media_group.append(InputMediaPhoto(media=m.file_id))
        if m.type == "video": media_group.append(InputMediaVideo(media=m.file_id))
    media_group[0].caption = messages.card_info(card)
    return await message.answer_media_group(media_group)


async def _send_card_with_single_media(message: AIOgramMessage, card: Card, keyboard: InlineKeyboard | ReplyKeyboard) -> AIOgramMessage:
    media = card.media[0]
    caption = messages.card_info(card)
    match(media.type):
        case "photo":
            return await message.answer_photo(
                photo=media.file_id,
                caption=caption,
                reply_markup=keyboard,
                parse_mode='HTML',
            )
        case "video":
            return await message.answer_video(
                video=media.file_id,
                caption=caption,
                reply_markup=keyboard,
                parse_mode='HTML',
            )
        case _:
            return None