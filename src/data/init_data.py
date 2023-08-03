from data.models import Character, Room, Mobile, MobileType, RoomConnection, Direction
from config import ENGINE
from sqlalchemy.orm import Session
import logging

with Session(ENGINE) as session:
    r1 = Room.create_room(session, 'This is the deepest darkest void.')
    r2 = Room.create_room(session, 'You\'ve gone into the light.')
    Direction.create_direction(session, 'east', 'west')
    RoomConnection.create_bidirectional_connection(session, r1, r2, 'east') 
    MobileType.add_type(session, 'monster')
    Mobile.create_mobile(session, 'a big stinky green goblin', 'monster', 1)
    Character.create_character(session, 'Rha', 1)
    logging.info(Room.get_exits(session, r1.id))
