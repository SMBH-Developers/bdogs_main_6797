from datetime import date, datetime
from typing import Literal
from sqlalchemy import BIGINT, TIMESTAMP, DATE, func, String, text
from sqlalchemy.orm import declarative_base, Mapped, mapped_column, DeclarativeBase



__all__ = ["Base", "User", "Shift", "Card", "Managers"]


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(BIGINT, primary_key=True)
    registration_date: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now())

    get_message: Mapped[bool] = mapped_column(server_default=text('false'))
    folder: Mapped[str | None] = mapped_column(String(16))
    ping_step: Mapped[Literal['FIRST', 'SECOND', 'THIRD'] | None] = mapped_column(String(16))


class Shift(Base):
    __tablename__ = 'shifts'

    date: Mapped[date] = mapped_column(DATE, primary_key=True)
    managers: Mapped[str] = mapped_column(String(25))


class Card(Base):
    __tablename__ = 'cards'

    card: Mapped[int] = mapped_column(BIGINT, primary_key=True)
    status: Mapped[str] = mapped_column(String(128), comment='Card like 1234567891234567')


class Managers(Base):
    __tablename__ = 'managers_list'

    id: Mapped[int] = mapped_column(BIGINT, autoincrement=True, primary_key=True)
    prefix_name: Mapped[str] = mapped_column(String(16)) # Ек Ди Су Ек2 Ка Ан Эл Та Ве Стас
