from datetime import date, datetime

from sqlalchemy import BIGINT, TIMESTAMP, DATE, func, String
from sqlalchemy.orm import declarative_base, Mapped, mapped_column


__all__ = ["Base", "User", "Shift", "Card"]


Base = declarative_base()


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(BIGINT, primary_key=True)
    registration_date: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now())


class Shift(Base):
    __tablename__ = 'shifts'

    date: Mapped[date] = mapped_column(DATE, primary_key=True)
    managers: Mapped[str] = mapped_column(String(5))


class Card(Base):
    __tablename__ = 'cards'

    card: Mapped[int] = mapped_column(BIGINT, primary_key=True)
    status: Mapped[str] = mapped_column(String(128), comment='Card like 1234567891234567')
