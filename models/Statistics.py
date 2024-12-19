from dataclasses import dataclass

@dataclass
class Statistics:
    users_count: int
    active_users_count: int
    cards_count: int
    male_count: int
    female_count: int
    users_who_liked_count: int
    users_who_messaged_count: int
    total_likes_count: int
    total_messages_count: int
