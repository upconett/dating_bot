from logic.abstract.user import UserWriter
from logic.static import UserAdapter

from models import User

from controllers.exceptions import NoDataInCache
from logic.exceptions import UserNotFound, SettingsNotCreated


class DefaultUserWriter(UserWriter):

    COUNT_USERS_QUERY = "SELECT COUNT(*) FROM users;"
    BIT_STRING_LENGTH_QUERY = """
        SELECT LENGTH(bit_string)
        FROM seen_cards
        LIMIT 1;
    """
    INCREASE_BITSTRING_QUERY = """
        UPDATE seen_cards
        SET bit_string = bit_string || '{concat}';
    """
    GET_USER_ID_QUERY = """
        SELECT id FROM users
        WHERE tg_id = {tg_id};
    """

    async def create(self, user: User) -> None:
        bit_string_length = await self.__get_current_bit_string_length()
        bit_string_length = await self.__double_bit_string_if_needed(bit_string_length)        # doubles for all users in db!
        await self.db.insert(
            table="users",
            data={
                "tg_id": user.tg_id,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "username": user.username
            }
        )
        await self.db.insert(
            table="seen_cards",
            data={
                "user_id": user.tg_id,
                "bit_string": '0'*bit_string_length
            }
        )
        if user.settings:
            await self.db.insert(
                table="settings",
                data={
                    "user_id": user.tg_id,
                    "seek_age_from": user.settings.seek_age_from,
                    "seek_age_to": user.settings.seek_age_to,
                    "seek_sex": user.settings.seek_sex.value,
                }
            )
        user.id = await self._get_generated_user_id(user)
        await self.cache.set_data(f"tg_id:{user.tg_id}", UserAdapter.to_dict(user))
        await self.cache.set_data(f"id:{user.id}", user.tg_id)

    
    async def update(self, user: User) -> None:
        user_update_status = await self.db.update(
            table="users",
            filter_by={"tg_id": user.tg_id},
            data={
                "first_name": user.first_name,
                "last_name": user.last_name,
                "username": user.username,
                "likes_left": user.likes_left,
                "bonus_likes": user.bonus_likes,
                "messages_left": user.messages_left,
                "bonus_messages": user.bonus_messages,
                "banned": user.banned
            }
        )
        settings_update_status = await self.db.update(
            table="settings",
            filter_by={"user_id": user.tg_id},
            data={
                "seek_age_from": user.settings.seek_age_from,
                "seek_age_to": user.settings.seek_age_to,
                "seek_sex": user.settings.seek_sex.value,
            }
        )

        if user_update_status == False:
            raise UserNotFound()
        if settings_update_status == False:
            settings_insert_status = await self.db.insert(
                table="settings",
                data={
                    "user_id": user.tg_id,
                    "seek_age_from": user.settings.seek_age_from,
                    "seek_age_to": user.settings.seek_age_to,
                    "seek_sex": user.settings.seek_sex.value,
                }   
            )
            if settings_insert_status == False:
                raise SettingsNotCreated()


        await self.cache.set_data(f"tg_id:{user.tg_id}", UserAdapter.to_dict(user))
        await self.cache.set_data(f"id:{user.id}", user.tg_id)

    async def add_liked(self, user: User, use_bonus: bool) -> None:
        try:
            cache_data = await self.cache.get_data(f"tg_id:{user.tg_id}")
            if use_bonus: cache_data['bonus_likes'] -= 1
            else: cache_data['likes_left'] -= 1
            await self.cache.set_data(f"tg_id:{user.tg_id}", cache_data)
        except NoDataInCache:
            pass

        column = "likes_left"
        if use_bonus:
            column = "bonus_likes"
        
        await self.db.custom_query(
            "update users set "
            "liked_today = liked_today + 1, "
            f"{column} = {column} - 1 "
            f"where id = {user.id};"
        )
    
    async def add_messaged(self, user: User, use_bonus: bool) -> None:
        try:
            cache_data = await self.cache.get_data(f"tg_id:{user.tg_id}")
            if use_bonus: cache_data['bonus_messages'] -= 1
            else: cache_data['messages_left'] -= 1
            await self.cache.set_data(f"tg_id:{user.tg_id}", cache_data)
        except NoDataInCache:
            pass

        column = "messages_left"
        if use_bonus:
            column = "bonus_messages"

        await self.db.custom_query(
            "update users set "
            "messaged_today = messaged_today + 1, "
            f"{column} = {column} - 1 "
            f"where id = {user.id};"
        )

    async def reset_likes_and_messages(self) -> None:
        await self.db.custom_query(
            "update users set "
            "liked_today = 0, messaged_today = 0, "
            "likes_left = 0, messages_left = 2; "
        )
    
    async def delete(self, user: User) -> None:
        await self.db.delete(
            table="users",
            filter_by={"tg_id": user.tg_id},
        )
        await self.db.delete(
            table="settings",
            filter_by={"user_id": user.tg_id},
        )
        await self.db.delete(
            table="cards",
            filter_by={"user_id": user.tg_id},
        )

        await self.cache.remove_key(f"tg_id:{user.tg_id}")
        await self.cache.remove_key(f"id:{user.id}")


    async def __get_current_bit_string_length(self) -> int:
        result = await self.db.custom_query(
            self.BIT_STRING_LENGTH_QUERY
        )
        if len(result) > 0:
            return result[0][0] or 10
        else:
            return 10


    async def __double_bit_string_if_needed(self, bitstr_len: int) -> int:
        users_amount = await self.__count_users()
        if self.__bitstring_needs_to_be_doubled(bitstr_len, users_amount):
            await self.__double_bitstring_for_all_users(bitstr_len)
            return bitstr_len * 2
        else:
            return bitstr_len

    async def __count_users(self) -> int:
        result = await self.db.custom_query(
            self.COUNT_USERS_QUERY
        )
        return result[0][0]

    def __bitstring_needs_to_be_doubled(self, bitstr_len: int, users_amount: int) -> int:
        return (bitstr_len - users_amount) < 10


    async def __double_bitstring_for_all_users(self, bitstr_len: int):
        await self.db.custom_query(
            self.INCREASE_BITSTRING_QUERY.format(concat="0"*bitstr_len)
        )

    async def _get_generated_user_id(self, user: User) -> int:
        result = await self.db.custom_query(
            self.GET_USER_ID_QUERY.format(tg_id=user.tg_id)
        )
        if result:
            return result[0][0]
        else:
            return 1
