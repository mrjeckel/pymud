from __future__ import annotations

import logging
import hashlib

from typing import Optional, List, Tuple
from sqlalchemy import (ForeignKey,
                        UniqueConstraint,
                        select,
                        update)
from sqlalchemy.types import String
from sqlalchemy.orm import (DeclarativeBase,
                            Mapped,
                            mapped_column,
                            validates)
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm.session import Session
from sqlalchemy.orm.exc import (MultipleResultsFound,
                                NoResultFound)
from exceptions import (LoginError,
                        CharacterExists,
                        BadRoomConnection)

class Base(DeclarativeBase):
    pass

class MudObject(Base):
    __tablename__ = 'mud_object'
    id: Mapped[int] = mapped_column(primary_key=True)
    short_desc: Mapped[str] = mapped_column(String(32), nullable=False)
    long_desc: Mapped[Optional[str]] = mapped_column(String(255))

class Item(MudObject):
    __tablename__ = 'item'
    id: Mapped[int] = mapped_column(ForeignKey('mud_object.id'), primary_key=True)
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
    mobile_type: Mapped[int] = mapped_column(ForeignKey('mobile_type.name'))
    room_id: Mapped[int] = mapped_column(ForeignKey('room.id'))

    __mapper_args__ = {
        'inherit_condition': (id == MudObject.id)
    }

    @classmethod
    def create_mobile(cls,
                      session: Session,
                      short_desc: str,
                      mobile_type: str,
                      room_id: int,
                      long_desc=None):
        mobile = Mobile(short_desc=short_desc,
                        mobile_type=mobile_type,
                        room_id=room_id,
                        long_desc=long_desc)
        session.add(mobile)
        session.commit()
        return mobile

    @classmethod
    def delete_mobile(cls, session: Session, id: int):
        session.execute(
            select(Mobile).where(Mobile.id == id)
            ).delete()
        session.commit()

class MobileType(Base):
    __tablename__ = 'mobile_type'
    name: Mapped[str] = mapped_column(String(32), primary_key=True)

    @classmethod
    def add_type(cls, session: Session, type_name: str):
        mobile_type = MobileType(name=type_name)
        session.add(mobile_type)
        session.commit()

class Direction(Base):
    __tablename__ = 'direction'
    name: Mapped[str] = mapped_column(String(10), primary_key=True)
    inverse: Mapped[str] = mapped_column(String(10))

    @classmethod
    def create_direction(cls, session: Session, direction: str, inverse: str):
        directions = [
            Direction(name=direction, inverse=inverse),
            Direction(name=inverse, inverse=direction)
        ]
        session.add_all(directions)
        session.commit()

class Room(MudObject):
    __tablename__ = 'room'
    id: Mapped[int] = mapped_column(ForeignKey('mud_object.id'), primary_key=True)

    @classmethod
    def create_room(cls, session: Session, short_desc: str, long_desc: str) -> Room:
        room = Room(short_desc=short_desc, long_desc=long_desc)
        session.add(room)
        session.commit()
        return room
    
    @classmethod
    def get_exits(cls, session: Session, room_id: int) -> List[str]:
        return session.execute(
            select(RoomConnection.direction).where(RoomConnection.room_id == room_id)
            ).scalars().all()
    
    @classmethod
    def get_desc(cls, session: Session, room_id: int) -> Tuple[str, str]:
        return session.execute(
            select(Room.short_desc, Room.long_desc).where(Room.id == room_id)
            ).scalar_one()
    
    @classmethod
    def get_occupants(cls, session: Session, room_id: int) -> List[int]:
        return session.execute(
            select(Character.id).where(Character.room_id == room_id)
            ).scalars().all()
    
    @classmethod
    def get_character_id(cls, session: Session, character_name: str, room_id: int) -> int:
        return session.execute(
            select(Character.id).where(
                (Character.name == character_name) &
                (Character.room_id == room_id))
            ).scalar_one()
    
    @classmethod
    def match_short_desc(cls, session: Session, short_desc: str, room_id: int) -> List[int]:
        return session.execute(
            select(MudObject.id).where(
                (MudObject.short_desc.contains(short_desc)) &
                (MudObject.parent == room_id))
            ).scalars.all()
    

class RoomConnection(Base):
    __tablename__ = 'room_connection'
    id: Mapped[int] = mapped_column(primary_key=True)
    room_id: Mapped[int] = mapped_column(ForeignKey('room.id'))
    destination_id: Mapped[int] = mapped_column(ForeignKey('room.id'))
    direction: Mapped[str] = mapped_column(ForeignKey('direction.name'))

    UniqueConstraint('room_id', 'destination_id')

    @classmethod
    def create_bidirectional_connection(cls,
                                        session: Session,
                                        room_id: int,
                                        destination_id: int,
                                        direction: str) -> List[RoomConnection]:
        inverse = session.execute(
            select(Direction.inverse).where(Direction.name == direction)
            ).scalar_one()
        connections = [ 
            RoomConnection(room_id=room_id,
                           destination_id=destination_id,
                           direction=direction),
            RoomConnection(room_id=destination_id,
                           destination_id=room_id,
                           direction=inverse)
        ]
        session.add_all(connections)
        session.commit()
        return connections
    
    @classmethod
    def create_unidirectional_connection(cls,
                                         session: Session,
                                         room_id: int,
                                         destination_id: int,
                                         direction) -> RoomConnection:
        connection = RoomConnection(room_id=room_id,
                                    destination_id=destination_id,
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

    __mapper_args__ = {
        'inherit_condition': (id == MudObject.id)
    }

    @classmethod
    def validate_account(cls, session: Session, character: Character, hash: str):
        try:
            account_hash = session.execute(
                select(Character.account_hash).where(Character.name == character)
                ).scalar_one()
        except (NoResultFound, MultipleResultsFound) as e:
            logging.exception(e)
            raise LoginError from e
        return hashlib.sha256(hash.encode('utf-8')).hexdigest() == account_hash
    
    @classmethod
    def create_character(cls,
                         session: Session,
                         name: str,
                         hash: str,
                         short_desc: str,
                         room_id: int=1):
        try:
            character = Character(name=name, account_hash=hash, short_desc=short_desc, room_id=room_id)
            session.add(character)
            session.commit()
        except IntegrityError as e:
            logging.exception(e)
            raise CharacterExists from e
        return character
    
    @classmethod
    def get_character(cls, session: Session, name):
        return session.execute(
            select(Character).where(Character.name == name)
            ).scalar_one()
    
    @classmethod
    def move(cls, session: Session, character: Character, direction: str):
        try:
            new_room = session.execute(
                select(RoomConnection.destination_id).where(
                    (RoomConnection.room_id == character.room_id) &
                    (RoomConnection.direction == direction)
                )).scalar_one()
            session.execute(
                update(Character).where(Character.id == character.id).values(room_id=new_room)
                )
            session.commit()
        except (NoResultFound, MultipleResultsFound) as e:
            raise BadRoomConnection from e
        
    @classmethod
    def refresh(cls, session: Session, character_id: int):
        return session.execute(
            select(Character).where(Character.id == character_id)
        ).scalar_one()
        
    @validates('account_hash')
    def _hash_password(self, _, hash: bytes):
        return hashlib.sha256(str(hash).encode('utf-8')).hexdigest()
