from data.models import Character, Room, Mobile, MobileType, RoomConnection, Direction
import logging

r1 = Room.create_room('This is the deepest darkest void.')
r2 = Room.create_room('You\'ve gone into the light.')
Direction.create_direction('east', 'west')
RoomConnection.create_bidirectional_connection(r1, r2, 'east') 
MobileType.add_type('monster')
Mobile.create_mobile('a big stinky green goblin', 'monster', 1)
Character.create_character('Rha', '1')
logging.info(Room.get_exits(r1))
