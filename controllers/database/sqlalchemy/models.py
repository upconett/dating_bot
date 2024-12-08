from typing import List, Optional

from controllers.database.sqlalchemy.Base import Base
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey


class User(Base):
    __tablename__ = "users"

    tg_id: Mapped[int] = mapped_column(primary_key=True)
    internal_id: Mapped[int] = mapped_column(autoincrement=True)
    first_name: Mapped[str] = mapped_column(nullable=False)
    last_name: Mapped[Optional[str]] = mapped_column(nullable=True)
    username: Mapped[Optional[str]] = mapped_column(nullable=True)

    settings: Mapped["Settings"] = relationship(back_populates="user")
    card: Mapped["Card"] = relationship(back_populates="user")


class Settings(Base):
    __tablename__ = "settings"

    user_id: Mapped[int] = mapped_column(ForeignKey("users.tg_id"), primary_key=True)
    seek_age_from: Mapped[int] = mapped_column(nullable=False)
    seek_age_to: Mapped[Optional[int]] = mapped_column(nullable=True)
    seek_sex: Mapped[bool] = mapped_column(nullable=False)

    user: Mapped["User"] = relationship()


class Card(Base):
    __tablename__ = "cards"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.tg_id"), nullable=False)
    name: Mapped[str] = mapped_column(nullable=False)
    age: Mapped[int] = mapped_column(nullable=False)
    city: Mapped[str] = mapped_column(nullable=False)
    sex: Mapped[bool] = mapped_column(nullable=False)
    interests: Mapped[str] = mapped_column(nullable=False, default="0"*20)
    description: Mapped[Optional[str]] = mapped_column()

    media: Mapped[List["Media"]] = relationship(back_populates="card")
    user: Mapped["User"] = relationship()

    def __repr__(self) -> str:
        return f"Card(id={self.id}, user_id={self.user_id})"

    
class Media(Base):
    __tablename__ = "card_media"

    id: Mapped[int] = mapped_column(primary_key=True)
    card_id: Mapped[int] = mapped_column(ForeignKey("cards.id"), primary_key=True)
    type: Mapped[str] = mapped_column(nullable=False)

    card: Mapped["Card"] = relationship()


class Like(Base):
    __tablename__ = "likes"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    sender_id: Mapped[int] = mapped_column(ForeignKey("users.tg_id"), nullable=False)
    receiver_id: Mapped[int] = mapped_column(ForeignKey("users.tg_id"), nullable=False)

    sender: Mapped["User"] = relationship(foreign_keys=[sender_id])
    receiver: Mapped["User"] = relationship(foreign_keys=[receiver_id])


class Transaction(Base):
    __tablename__ = "transactions"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.tg_id"), nullable=False)
    price: Mapped[int] = mapped_column(nullable=False)
    product: Mapped[str] = mapped_column(nullable=False)

    user: Mapped["User"] = relationship()
