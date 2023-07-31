from data.models import Character, Room, Mobile, MobileType

Room.create_room('This is the deepest darkest void.')
MobileType.add_type('monster')
Mobile.create_mobile('a big stinky green goblin', 'monster', 1)
Character.create_character('Rha', '1')
