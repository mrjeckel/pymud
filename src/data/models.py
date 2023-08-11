import logging
import hashlib
from typing import Optional
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
    parent: Mapped[int] = mapped_column(ForeignKey('mud_object.id'))

class Item(MudObject):
    __tablename__ = 'item'
    id: Mapped[int] = mapped_column(ForeignKey('mud_object.id'), primary_key=True)
    short_desc: Mapped[str] = mapped_column(ForeignKey('mud_object.short_desc'))
    long_desc: Mapped[str] = mapped_column(ForeignKey('mud_object.long_desc'))
    item_type: Mapped[int] = mapped_column(ForeignKey('item_type.name'))
    parent: Mapped[int] = mapped_column(ForeignKey('mud_object.parent'))

    __mapper_args__ = {
        'inherit_condition': (id == MudObject.id)
    }

class ItemType(Base):
    __tablename__ = 'item_type'
    name: Mapped[str] = mapped_column(String(32), primary_key=True)

class Mobile(MudObject):
    __tablename__ = 'mobile'
    id: Mapped[int] = mapped_column(ForeignKey('mud_object.id'), primary_key=True)
    short_desc: Mapped[str] = mapped_column(ForeignKey('mud_object.short_desc'))
    long_desc: Mapped[str] = mapped_column(ForeignKey('mud_object.long_desc'))
    mobile_type: Mapped[int] = mapped_column(ForeignKey('mobile_type.name'))
    room_id: Mapped[int] = mapped_column(ForeignKey('mud_object.parent'))

    @classmethod
    def create_mobile(cls, session, short_desc, mobile_type, room_id, long_desc=None):
        mobile = Mobile(short_desc=short_desc,
                        mobile_type=mobile_type,
                        room_id=room_id,
                        long_desc=long_desc)
        session.add(mobile)
        session.commit()
        return mobile

    @classmethod
    def delete_mobile(cls, session, id):
        session.execute(
            select(Mobile).where(Mobile.id == id)
            ).delete()
        session.commit()

class MobileType(Base):
    __tablename__ = 'mobile_type'
    name: Mapped[str] = mapped_column(String(32), primary_key=True)

    @classmethod
    def add_type(cls, session, type_name):
        mobile_type = MobileType(name=type_name)
        session.add(mobile_type)
        session.commit()

class Direction(Base):
    __tablename__ = 'direction'
    name: Mapped[str] = mapped_column(String(10), primary_key=True)
    inverse: Mapped[str] = mapped_column(String(10))

    @classmethod
    def create_direction(cls, session, direction, inverse):
        directions = [
            Direction(name=direction, inverse=inverse),
            Direction(name=inverse, inverse=direction)
        ]
        session.add_all(directions)
        session.commit()

class Room(MudObject):
    __tablename__ = 'room'
    id: Mapped[int] = mapped_column(ForeignKey('mud_object.id'), primary_key=True)
    desc: Mapped[str] = mapped_column(String(255))

    @classmethod
    def create_room(cls, session, desc):
        room = Room(desc=desc)
        session.add(room)
        session.commit()
        return room
    
    @classmethod
    def get_exits(cls, session, room_id):
        return session.execute(
            select(RoomConnection.direction).where(RoomConnection.room_id == room_id)
            ).scalars().all()
    
    @classmethod
    def get_desc(cls, session, character):
        return session.execute(
            select(Room.desc).where(Room.id == character.room_id)
            ).scalar_one()
    
    @classmethod
    def get_occupants(cls, session, room_id):
        return session.execute(
            select(Character.id).where(Character.room_id == room_id)
            ).scalars().all()
    
    @classmethod
    def get_character_id(cls, session, character_name, room_id):
        return session.execute(
            select(Character.id).where(
                (Character.name == character_name) &
                (Character.room_id == room_id))
            ).scalar_one()
    
    @classmethod
    def match_short_desc(cls, session, short_desc, room_id):
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
    def create_bidirectional_connection(cls, session, room, destination, direction):
        inverse = session.execute(
            select(Direction.inverse).where(Direction.name == direction)
            ).scalar_one()
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
    
    @classmethod
    def create_unidirectional_connection(cls, session, room, destination, direction):
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
    room_id: Mapped[int] = mapped_column(ForeignKey('mud_object.parent'))
    short_desc: Mapped[str] = mapped_column(ForeignKey('mud_object.short_desc'))
    long_desc: Mapped[str] = mapped_column(ForeignKey('mud_object.long_desc'))

    @classmethod
    def validate_account(cls, session, character, hash):
        try:
            account_hash = session.execute(
                select(Character.account_hash).where(Character.name == character)
                ).scalar_one()
        except (NoResultFound, MultipleResultsFound) as e:
            logging.exception(e)
            raise LoginError from e
        return hashlib.sha256(hash.encode('utf-8')).hexdigest() == account_hash
    
    @classmethod
    def create_character(cls, session, name, hash, room=1):
        try:
            character = Character(name=name, account_hash=hash, room_id=room)
            session.add(character)
            session.commit()
        except IntegrityError as e:
            logging.exception(e)
            raise CharacterExists from e
        return character
    
    @classmethod
    def get_character(cls, session, name):
        return session.execute(
            select(Character).where(Character.name == name)
            ).scalar_one()
    
    @classmethod
    def move(cls, session, character, direction):
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
    def refresh(cls, session, character):
        return session.execute(
            select(Character).where(Character.id == character.id)
        ).scalar_one()
        
    @validates('account_hash')
    def _hash_password(self, _, hash):
        return hashlib.sha256(str(hash).encode('utf-8')).hexdigest()
