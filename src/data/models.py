import bcrypt
from sqlalchemy import ForeignKey
from sqlalchemy.types import Integer, String
from sqlalchemy.orm import (DeclarativeBase,
                            Mapped,
                            mapped_column,
                            validates)

class Base(DeclarativeBase):
    pass

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

class Direction(Base):
    __tablename__ = 'direction'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    dirn_name: Mapped[str] = mapped_column(String(10), unique=True)

class Room(Base):
    __tablename__ = 'room'
    id: Mapped[int] = mapped_column(primary_key=True)
    desc: Mapped[str] = mapped_column(String(255))

class RoomConnection(Base):
    __tablename__ = 'room_connection'
    id: Mapped[int] = mapped_column(primary_key=True)
    direction: Mapped[str] = mapped_column(ForeignKey('direction.dir_name'))
    room_id: Mapped[str] = mapped_column(ForeignKey('room.id'))
    destination_id: Mapped[str] = mapped_column(ForeignKey('room.id'))

class Character(Base):
    __tablename__ = 'character'
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(16))
    password: Mapped[str] = mapped_column(String(60))

    def validate_password(self, password):
        return bcrypt.checkpw(password, self.password)
    
    @validates('password')
    def _hash_password(self, password):
        salt = bcrypt.gensalt()
        return bcrypt.hashpw(password, salt)
