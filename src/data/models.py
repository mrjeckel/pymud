from typing import List
from sqlalchemy import Table, Column, ForeignKey
from sqlalchemy.types import Integer, String
from sqlalchemy.orm import (DeclarativeBase,
                            Mapped,
                            mapped_column,
                            relationship)

class Base(DeclarativeBase):
    pass

room_exit_association = Table(
    'room_exit',
    Base.metadata,
    Column('room_id', Integer, ForeignKey('room.id')),
    Column('exit_id', Integer, ForeignKey('exit.id')),
    )
    
class Item(Base):
    __tablename__ = 'item'
    id: Mapped[int] = mapped_column(primary_key=True)
    short_desc: Mapped[str] = mapped_column(String(32), nullable=False)
    long_desc: Mapped[str] = mapped_column(String(255))
    item_type: Mapped[int] = mapped_column(ForeignKey('item_type.id'))
    room: Mapped[int] = mapped_column(ForeignKey('room.id'))

class ItemType(Base):
    __tablename__ = 'item_type'
    id: Mapped[int] = mapped_column(primary_key=True)
    type_name: Mapped[str] = mapped_column(String(32), unique=True)

class Mobile(Base):
    __tablename__ = 'mobile'
    id: Mapped[int] = mapped_column(primary_key=True)
    short_desc: Mapped[str] = mapped_column(String(32), nullable=False)
    long_desc: Mapped[str] = mapped_column(String(255))
    mobile_type: Mapped[int] = mapped_column(ForeignKey('mobile_type.id'))
    room: Mapped[int] = mapped_column(ForeignKey('room.id'))

class MobileType(Base):
    __tablename__ = 'mobile_type'
    id: Mapped[int] = mapped_column(primary_key=True)
    type_name: Mapped[str] = mapped_column(String(32), unique=True)

class Exit(Base):
    __tablename__ = 'exit'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    exit_name: Mapped[str] = mapped_column(String(12), unique=True)

class Room(Base):
    __tablename__ = 'room'
    id: Mapped[int] = mapped_column(primary_key=True)
    desc: Mapped[str] = mapped_column(String(255))
    exits: Mapped[List[Exit]] = relationship(secondary='room_exit_association')
