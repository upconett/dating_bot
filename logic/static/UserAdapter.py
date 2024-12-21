from telegram import AIOgramChat

from models import User, Settings, Sex


class UserAdapter:

    @staticmethod
    def from_dict(data: dict) -> User:
        return User(
            id=data.get("id"),
            tg_id=data.get("tg_id"),
            first_name=data.get("first_name"),
            last_name=data.get("last_name"),
            username=data.get("username"),
            settings=UserAdapter._settings_from_dict(data),
            likes_left=data.get("likes_left") or 0,
            bonus_likes=data.get("bonus_likes") or 0,
            messages_left=data.get("messages_left") or 0,
            bonus_messages=data.get("bonus_messages") or 0,
            banned=data.get("banned") or False,
        )

    
    @staticmethod
    def to_dict(user: User) -> dict:
        settings_dict = UserAdapter._settings_to_dict(user.settings)
        return {
            "id": user.id,
            "tg_id": user.tg_id,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "username": user.username,
            "settings": settings_dict,
            "likes_left": user.likes_left,
            "bonus_likes": user.bonus_likes,
            "messages_left": user.messages_left,
            "bonus_messages": user.bonus_messages,
            "banned": user.banned,
        }

    
    @staticmethod
    def _settings_from_dict(data: dict) -> Settings | None:
        dict_settings: dict = data.get("settings")
        if dict_settings:
            return Settings(
                seek_age_from=dict_settings.get("seek_age_from"),
                seek_age_to=dict_settings.get("seek_age_to"),
                seek_sex=Sex(dict_settings.get("seek_sex"))
            )
        else:
            return None
        
    
    @staticmethod
    def _settings_to_dict(settings: Settings) -> dict | None:
        if settings is None: return None
        return {
            "seek_age_from": settings.seek_age_from,
            "seek_age_to": settings.seek_age_to,
            "seek_sex": settings.seek_sex.value
        }



    @staticmethod
    def from_aiogram_chat(chat: AIOgramChat) -> User:
        return User(
            id=-1,
            tg_id=chat.id,
            first_name=chat.first_name,
            last_name=chat.last_name,
            username=chat.username,
            settings = None,
            likes_left=20,
            bonus_likes=0,
            messages_left=2,
            bonus_messages=0,
        )
