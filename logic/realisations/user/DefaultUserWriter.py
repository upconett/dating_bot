from logic.abstract.user import UserWriter

from models import User


class DefaultUserWriter(UserWriter):
    async def create(self, user: User) -> None:
        await self.db.insert(
            table="users",
            data={
                "tg_id": user.id,
                "first_name": user.first_name,
                "last_name": user.last_name,
                "username": user.username
            }
        )
        await self.db.insert(
            table="settings",
            data={
                "user_id": user.id,
                "seek_age_from": user.settings.seek_age_from,
                "seek_age_to": user.settings.seek_age_to,
                "seek_sex": user.settings.seek_sex.value,
            }   
        )

    
    async def update(self, user: User) -> None:
        await self.db.update(
            table="users",
            filter_by={"tg_id": user.id},
            data={
                "first_name": user.first_name,
                "last_name": user.last_name,
                "username": user.username
            }
        )
        await self.db.update(
            table="settings",
            filter_by={"user_id": user.id},
            data={
                "seek_age_from": user.settings.seek_age_from,
                "seek_age_to": user.settings.seek_age_to,
                "seek_sex": user.settings.seek_sex.value,
            }
        )

    
    async def delete(self, user: User) -> None:
        await self.db.delete(
            table="users",
            filter_by={"tg_id": user.id},
        )
        await self.db.delete(
            table="settings",
            filter_by={"user_id": user.id},
        )
        await self.db.delete(
            table="cards",
            filter_by={"user_id": user.id},
        )
