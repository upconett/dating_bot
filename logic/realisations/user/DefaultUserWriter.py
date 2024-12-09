from logic.abstract.user import UserWriter
from logic.static import UserAdapter

from models import User

from logic.exceptions import UserNotFound, SettingsNotCreated


class DefaultUserWriter(UserWriter):
    async def create(self, user: User) -> None:
        await self.db.insert(
            table="users",
            data={
                "tg_id": user.tg_id,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "username": user.username
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
        await self.cache.set_data(f"tg_id:{user.tg_id}", UserAdapter.to_dict(user))
        await self.cache.set_data(f"id:{user.id}", user.tg_id)

    
    async def update(self, user: User) -> None:
        user_update_status = await self.db.update(
            table="users",
            filter_by={"tg_id": user.tg_id},
            data={
                "first_name": user.first_name,
                "last_name": user.last_name,
                "username": user.username
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
