import logging
import hashlib
from typing import Optional, List
from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.types import Integer, String
from sqlalchemy.orm import (DeclarativeBase,
                            Mapped,
                            mapped_column,
                            validates,
                            sessionmaker,
                            relationship)
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.exc import (MultipleResultsFound,
                                NoResultFound)
from config import ENGINE
from exceptions import (LoginError,
                           CharacterExists)

Session = sessionmaker(ENGINE, expire_on_commit=False)

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
    item_type: Mapped[int] = mapped_column(ForeignKey('item_type.name'))
    parent: Mapped[int] = mapped_column(ForeignKey('mud_object.id'))

    __mapper_args__ = {
        'inherit_condition': (id == MudObject.id)
    }

class ItemType(Base):
    __tablename__ = 'item_type'
    name: Mapped[str] = mapped_column(String(32), primary_key=True)

class Mobile(MudObject):
    __tablename__ = 'mobile'
    id: Mapped[int] = mapped_column(ForeignKey('mud_object.id'), primary_key=True)
    short_desc: Mapped[str] = mapped_column(String(32), nullable=False)
    long_desc: Mapped[Optional[str]] = mapped_column(String(255))
    mobile_type: Mapped[int] = mapped_column(ForeignKey('mobile_type.name'))
    room_id: Mapped[int] = mapped_column(ForeignKey('room.id'))

    @classmethod
    def create_mobile(cls, short_desc, mobile_type, room_id, long_desc=None):
        with Session() as session:
            mobile = Mobile(short_desc=short_desc,
                            mobile_type=mobile_type,
                            room_id=room_id,
                            long_desc=long_desc)
            session.add(mobile)
            session.commit()
        return mobile

    @classmethod
    def delete_mobile(cls, id):
        with Session() as session:
            session.query(Mobile).where(Mobile.id == id).delete()
            session.commit()

class MobileType(Base):
    __tablename__ = 'mobile_type'
    name: Mapped[str] = mapped_column(String(32), primary_key=True)

    @classmethod
    def add_type(cls, type_name):
        with Session() as session:
            mobile_type = MobileType(name=type_name)
            session.add(mobile_type)
            session.commit()
        return mobile_type

class Direction(Base):
    __tablename__ = 'direction'
    name: Mapped[str] = mapped_column(String(10), primary_key=True)
    inverse: Mapped[str] = mapped_column(String(10))

    @classmethod
    def create_direction(cls, direction, inverse):
        with Session() as session:
            direction = Direction(name=direction, inverse=inverse)
            session.add(direction)
            session.commit()
        return direction

class Room(MudObject):
    __tablename__ = 'room'
    id: Mapped[int] = mapped_column(ForeignKey('mud_object.id'), primary_key=True)
    desc: Mapped[str] = mapped_column(String(255))

    @classmethod
    def create_room(cls, desc):
        with Session() as session:
            room = Room(desc=desc)
            session.add(room)
            session.commit()
        return room
    
    def exits(self):
        with Session() as session:
            exits = session.query(RoomConnection.direction).where(RoomConnection.room_id == self.id).all()
        return [exit for exit in exits]

class RoomConnection(Base):
    __tablename__ = 'room_connection'
    id: Mapped[int] = mapped_column(primary_key=True)
    room_id: Mapped[int] = mapped_column(ForeignKey('room.id'))
    destination_id: Mapped[int] = mapped_column(ForeignKey('room.id'))
    direction: Mapped[str] = mapped_column(ForeignKey('direction.name'))

    UniqueConstraint('room_id', 'destination_id')

    @classmethod
    def create_bidirectional_connection(cls, room, destination, direction):
        with Session() as session:
            inverse = session.query(Direction.inverse).where(Direction.name == direction).one()[0]
            connections = [ 
                RoomConnection(room_id=room.id,
                               destination_id=destination.id,
                               direction=direction),
                RoomConnection(room_id=destination.id,
                               destination_id=room.id,
                               direction=inverse)
            ]
            session.add_all(connections)
            session.commit()
        return connections
    
    def create_unidirectional_connection(cls, room, destination, direction):
        with Session() as session:
            connection = RoomConnection(room_id=room.id,
                                        destination_id=destination.id,
                                        direction=direction)
            session.add(connection)
            session.commit()
        return connection

class Character(MudObject):
    __tablename__ = 'character'
    id: Mapped[int] = mapped_column(ForeignKey('mud_object.id'), primary_key=True)
    name: Mapped[str] = mapped_column(String(16), unique=True)
    account_hash: Mapped[str] = mapped_column(String(64))
    room_id: Mapped[int] = mapped_column(ForeignKey('room.id'))

    @classmethod
    def validate_account(cls, character, hash):
        with Session() as session:
            try:
                account_hash = session.query(Character.account_hash).where(Character.name == character).one()[0]
            except (NoResultFound, MultipleResultsFound) as e:
                logging.exception(e)
                raise LoginError from e
        return hashlib.sha256(hash.encode('utf-8')).hexdigest() == account_hash
    
    @classmethod
    def create_character(cls, name, hash, room=1):
        with Session() as session:
            try:
                character = Character(name=name, account_hash=hash, room_id=room)
                session.add(character)
                session.commit()
            except IntegrityError as e:
                logging.exception(e)
                raise CharacterExists from e
        return character
        
    @validates('account_hash')
    def _hash_password(self, key, hash):
        return hashlib.sha256(hash.encode('utf-8')).hexdigest()
