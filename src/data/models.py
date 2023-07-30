import logging
import hashlib
from sqlalchemy import ForeignKey
from sqlalchemy.types import Integer, String
from sqlalchemy.orm import (DeclarativeBase,
                            Mapped,
                            mapped_column,
                            validates,
                            Session)
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import (MultipleResultsFound,
                                NoResultFound)
from pymud import MudServer
from exceptions import (LoginError,
                        CharacterExists)

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
    dir_name: Mapped[str] = mapped_column(String(10), unique=True)

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
    name: Mapped[str] = mapped_column(String(16), unique=True)
    account_hash: Mapped[str] = mapped_column(String(64))

    @classmethod
    def validate_account(cls, character, hash):
        with Session(MudServer.engine) as session:
            try:
                account_hash = session.query(Character.account_hash).where(Character.name == character).one()
            except (NoResultFound, MultipleResultsFound) as e:
                logging.exception(e)
                raise LoginError from e
        return hash == account_hash
    
    @classmethod
    def create_character(cls, name, hash):
        with Session(MudServer.engine) as session:
            try:
                session.add(Character(name=name, account_hash=hash))
                session.commit()
            except IntegrityError as e:
                logging.exception(e)
                raise CharacterExists from e
        
    @validates('account_hash')
    def _hash_password(self, key, hash):
        return hashlib.sha256(hash.encode('utf-8')).hexdigest()
