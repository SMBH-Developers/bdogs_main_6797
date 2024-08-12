from datetime import datetime

from sqlalchemy import BIGINT, TIMESTAMP, func
from sqlalchemy.orm import declarative_base, Mapped, mapped_column


__all__ = ["Base", "User"]


Base = declarative_base()


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(BIGINT, primary_key=True)
    registration_date: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now())
