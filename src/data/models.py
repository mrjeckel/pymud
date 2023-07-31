import logging
import hashlib
from typing import Optional
from sqlalchemy import ForeignKey
from sqlalchemy.types import Integer, String
from sqlalchemy.orm import (DeclarativeBase,
                            Mapped,
                            mapped_column,
                            validates,
                            Session,
                            relationship)
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import (MultipleResultsFound,
                                NoResultFound)
from config import ENGINE
from exceptions import (LoginError,
                           CharacterExists)

class Base(DeclarativeBase):
    pass

class MudObject(Base):
    __tablename__ = 'mud_object'
    id: Mapped[int] = mapped_column(primary_key=True)

class Item(MudObject):
    __tablename__ = 'item'
    id: Mapped[int] = mapped_column(ForeignKey('mud_object.id'), primary_key=True)
    short_desc: Mapped[str] = mapped_column(String(32), nullable=False)
    long_desc: Mapped[Optional[str]] = mapped_column(String(255))
    item_type: Mapped[int] = mapped_column(ForeignKey('item_type.id'))
    parent: Mapped[int] = mapped_column(ForeignKey('mud_object.id'))

    __mapper_args__ = {
        'inherit_condition': (id == MudObject.id)
    }

class ItemType(Base):
    __tablename__ = 'item_type'
    id: Mapped[int] = mapped_column(primary_key=True)
    type_name: Mapped[str] = mapped_column(String(32), unique=True)

class Mobile(MudObject):
    __tablename__ = 'mobile'
    id: Mapped[int] = mapped_column(ForeignKey('mud_object.id'), primary_key=True)
    short_desc: Mapped[str] = mapped_column(String(32), nullable=False)
    long_desc: Mapped[Optional[str]] = mapped_column(String(255))
    mobile_type: Mapped[int] = mapped_column(ForeignKey('mobile_type.id'))
    room_id: Mapped[int] = mapped_column(ForeignKey('room.id'))

    @classmethod
    def create_mobile(cls, short_desc, mobile_type, room_id, long_desc=None):
        with Session(ENGINE) as session:
            type_id = session.query(MobileType.id).where(MobileType.type_name == mobile_type).one()[0]
            session.add(Mobile(short_desc=short_desc,
                               mobile_type=type_id,
                               room_id=room_id,
                               long_desc=long_desc))
            session.commit()

    @classmethod
    def delete_mobile(cls, id):
        with Session(ENGINE) as session:
            session.query(Mobile).where(Mobile.id == id).delete()
            session.commit()

class MobileType(Base):
    __tablename__ = 'mobile_type'
    id: Mapped[int] = mapped_column(primary_key=True)
    type_name: Mapped[str] = mapped_column(String(32), unique=True)

    @classmethod
    def add_type(cls, type_name):
        with Session(ENGINE) as session:
            session.add(MobileType(type_name=type_name))
            session.commit()

class Direction(Base):
    __tablename__ = 'direction'
    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    dir_name: Mapped[str] = mapped_column(String(10), unique=True)

class Room(MudObject):
    __tablename__ = 'room'
    id: Mapped[int] = mapped_column(ForeignKey('mud_object.id'), primary_key=True)
    desc: Mapped[str] = mapped_column(String(255))

    @classmethod
    def create_room(cls, desc):
        with Session(ENGINE) as session:
            session.add(Room(desc=desc))
            session.commit()

class RoomConnection(Base):
    __tablename__ = 'room_connection'
    id: Mapped[int] = mapped_column(primary_key=True)
    direction: Mapped[str] = mapped_column(ForeignKey('direction.dir_name'))
    room_id: Mapped[str] = mapped_column(ForeignKey('room.id'))
    destination_id: Mapped[str] = mapped_column(ForeignKey('room.id'))

class Character(MudObject):
    __tablename__ = 'character'
    id: Mapped[int] = mapped_column(ForeignKey('mud_object.id'), primary_key=True)
    name: Mapped[str] = mapped_column(String(16), unique=True)
    account_hash: Mapped[str] = mapped_column(String(64))
    room_id: Mapped[int] = mapped_column(ForeignKey('room.id'))

    @classmethod
    def validate_account(cls, character, hash):
        with Session(ENGINE) as session:
            try:
                account_hash = session.query(Character.account_hash).where(Character.name == character).one()[0]
            except (NoResultFound, MultipleResultsFound) as e:
                logging.exception(e)
                raise LoginError from e
        return hashlib.sha256(hash.encode('utf-8')).hexdigest() == account_hash
    
    @classmethod
    def create_character(cls, name, hash, room=1):
        with Session(ENGINE) as session:
            try:
                session.add(Character(name=name, account_hash=hash, room_id=room))
                session.commit()
            except IntegrityError as e:
                logging.exception(e)
                raise CharacterExists from e
        
    @validates('account_hash')
    def _hash_password(self, key, hash):
        return hashlib.sha256(hash.encode('utf-8')).hexdigest()
