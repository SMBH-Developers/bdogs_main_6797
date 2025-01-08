from datetime import date, datetime
from typing import Literal, List
from sqlalchemy import (
    BIGINT,
    TIMESTAMP,
    DATE,
    func,
    String,
    text,
    ForeignKey,
    UniqueConstraint,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    DeclarativeBase,
    relationship,
)


__all__ = ["Base", "User", "Shift", "Card", "Managers"]


class Base(DeclarativeBase):
    is_deleted: Mapped[bool] = mapped_column(server_default=text('false'))


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(BIGINT, primary_key=True)
    registration_date: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now())

    get_message: Mapped[bool] = mapped_column(server_default=text('false'))
    folder: Mapped[str | None] = mapped_column(String(16))
    ping_step: Mapped[Literal['FIRST', 'SECOND', 'THIRD'] | None] = mapped_column(String(16))


class Card(Base):
    __tablename__ = 'cards'

    card: Mapped[int] = mapped_column(BIGINT, primary_key=True)
    status: Mapped[str] = mapped_column(String(128), comment='Card like 1234567891234567')


class Shift(Base):
    '''
    date: 2024-11-09
    managers: Ве Та Ан Су
    '''
    __tablename__ = 'shifts'
    
    id: Mapped[int] = mapped_column(BIGINT, autoincrement=True, primary_key=True)
    date: Mapped[date] = mapped_column(DATE)
    
    managers: Mapped[List['Managers']] = relationship(
        secondary='managers_shifts',
        back_populates='shifts',
        cascade='all',
        passive_deletes=True
    )

    __table_args__ = (
        UniqueConstraint('date', name='shift_date_key'),
    )


class Managers(Base):
    '''
    Старые имена: Ек Ди Су Ек2 Ка Ан Эл Та Ве Стас
    '''
    __tablename__ = 'managers_list'

    id: Mapped[int] = mapped_column(BIGINT, autoincrement=True, primary_key=True)
    prefix_name: Mapped[str] = mapped_column(String(16), unique=True)
    
    shifts: Mapped[List['Shift']] = relationship(
        secondary='managers_shifts',
        back_populates='managers',
        passive_deletes=True
    )


class ManagersShift(Base):
    __tablename__ = 'managers_shifts'

    shift_id: Mapped[int] = mapped_column(
        ForeignKey('shifts.id', ondelete='CASCADE'),
        primary_key=True
    )
    manager_id: Mapped[int] = mapped_column(
        ForeignKey('managers_list.id', ondelete='RESTRICT'),
        primary_key=True
    )
