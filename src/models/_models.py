from typing import Literal
from datetime import date, datetime, timedelta

from sqlalchemy import BIGINT, TIMESTAMP, DATE, func, String, Interval, text
from sqlalchemy.orm import declarative_base, Mapped, mapped_column


__all__ = ["Base", "User", "Shift", "Card", "ManagerList"]


Base = declarative_base()


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(BIGINT, primary_key=True)
    registration_date: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now())
    status: Mapped[Literal['alive', 'blocked']] = mapped_column(String(32), server_default='alive')

    folder: Mapped[str] = mapped_column(String(32))

    step: Mapped[str] = mapped_column(String(32), server_default='0-0')
    funnel: Mapped[str] = mapped_column(String(64), server_default='default_funnel')

    last_message_at_user: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now())
    last_message_at_bot: Mapped[datetime | None] = mapped_column(TIMESTAMP)

    being_late: Mapped[timedelta] = mapped_column(Interval, server_default=text("INTERVAL '0 second'"))


class Shift(Base):
    __tablename__ = 'shifts'

    date: Mapped[date] = mapped_column(DATE, primary_key=True)
    managers: Mapped[str] = mapped_column(String(25))


class Card(Base):
    __tablename__ = 'cards'

    card: Mapped[int] = mapped_column(BIGINT, primary_key=True)
    status: Mapped[str] = mapped_column(String(128), comment='Card like 1234567891234567')


class ManagerList(Base):
    __tablename__ = 'managers'

    id: Mapped[int] = mapped_column(BIGINT, autoincrement=True, primary_key=True)
    managers: Mapped[str] = mapped_column(String)
