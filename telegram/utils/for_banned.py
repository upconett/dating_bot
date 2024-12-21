from telegram import AIOgramMessage

from models import User


async def banned_handler(message: AIOgramMessage, user: User):
    await message.answer(
        "Вы были забанены ☠️\n"
        "Более вам не позволено пользоваться ботом"
    )
