from typing import List, Dict

from models import Card, Sex, Media


class CardAdapter:

    @staticmethod
    def from_dict(data: Dict, media_data: List[Dict]) -> Card:
        return Card(
            active=data.get("active") or True,
            id=data.get("id"),
            user_id=data.get("user_id"),
            name=data.get("name"),
            sex=Sex(data.get("sex")),
            age=data.get("age"),
            city=data.get("city"),
            interests=data.get("interests"),
            description=data.get("description"),
            media=CardAdapter.__media_from_dict(media_data)
        )

    @staticmethod
    def __media_from_dict(media_data: List[Dict]) -> List[Media]:
        return [Media(d.get("type"), d.get("id")) for d in media_data]

    