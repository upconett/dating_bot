from typing import List

from telegram import AIOgramQuery, StateFilter, F
from telegram import InputMediaPhoto, InputMediaVideo
from telegram import UpdateHandler, UpdateHandlerConfig
from telegram import FSMContext, States

from telegram.assets import messages, keyboards
from telegram import NotificationManager

from models import User, Card, Media

from services import UserService, StatService, PaymentService
from logic.exceptions import CardNotFound, InvalidUser


class PaymentHandler(UpdateHandler):
    notification_manager: NotificationManager
    user_service: UserService
    stat_service: StatService
    payment_service: PaymentService

    def __init__(
            self,
            config: UpdateHandlerConfig,
            notification_manager: NotificationManager,
            user_service: UserService,
            stat_service: StatService,
            payment_service: PaymentService
        ):
        super().__init__(config)
        self.notification_manager = notification_manager
        self.user_service = user_service
        self.stat_service = stat_service
        self.payment_service = payment_service

    async def send_like_payment_link(self, query: AIOgramQuery, user: User):
        payment = await self.payment_service.create_like_payment(user)
        await query.message.edit_text(
            text=messages.PAYMENT_LINK,
            reply_markup=keyboards.like_payment_with_url(payment)
        )

    async def send_message_payment_link(self, query: AIOgramQuery, user: User):
        payment = await self.payment_service.create_message_payment(user)
        await query.message.edit_text(
            text=messages.PAYMENT_LINK,
            reply_markup=keyboards.message_payment_with_url(payment)
        )

    async def check_like_payment(self, query: AIOgramQuery, user: User):
        payment_label = query.data.split("_")[2]
        if await self.payment_service.is_payment_successful(payment_label):
            await query.message.edit_text(
                text=messages.LIKE_PAYMENT_SUCCESS,
                reply_markup=None
            )
            await self.stat_service.add_bonus_likes(user)
            await self.notification_manager.log_like_payment(user)
        else:
            await query.answer("Оплата ещё не прошла ❌")


    async def check_message_payment(self, query: AIOgramQuery, user: User):
        payment_label = query.data.split("_")[2]
        if await self.payment_service.is_payment_successful(payment_label):
            await query.message.edit_text(
                text=messages.MESSAGE_PAYMENT_SUCCESS,
                reply_markup=None
            )
            await self.stat_service.add_bonus_messages(user)
            await self.notification_manager.log_message_payment(user)
        else:
            await query.answer("Оплата ещё не прошла ❌")


    async def cancel_payment(self, query: AIOgramQuery):
        await query.message.delete()

    def register_handlers(self):
        self.router.callback_query.register(self.cancel_payment, F.data == "cancel")
        self.router.callback_query.register(self.send_like_payment_link, F.data == "payment_like")
