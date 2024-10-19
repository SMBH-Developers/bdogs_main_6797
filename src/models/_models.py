from datetime import date, datetime

from sqlalchemy import BIGINT, TIMESTAMP, DATE, func, String
from sqlalchemy.orm import declarative_base, Mapped, mapped_column


__all__ = ["Base", "User", "Shift", "Card", "ManagerList"]


Base = declarative_base()


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(BIGINT, primary_key=True)
    registration_date: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now())

    folder: Mapped[str | None] = mapped_column(String(16))


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
