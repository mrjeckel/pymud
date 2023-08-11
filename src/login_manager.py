import json
import logging

from typing import Callable

from data.models import Character
from exceptions import LoginError

class LoginManager:
    def __init__(self, session, data, address: str, send_callback: Callable[[str], None]):
        self.success = False
        login_info = json.loads(data)

        try:
            if Character.validate_account(session, login_info['character_name'], login_info['account_hash']):
                send_callback(f'Welcome {login_info["character_name"]}!'.encode('utf-8'))
                logging.info(f'{login_info["character_name"]} succesfully authenticated - {address}')
                self.success = True
                self.character = Character.get_character(session, login_info['character_name'])
            else:
                send_callback(f'Invalid login credentials.'.encode('utf-8'))
                logging.info(f'Invalid login: {login_info["character_name"]} - {address}')
        except LoginError as e:
            send_callback(f'No character found by the name of {login_info["character_name"]}.'.encode('utf-8'))
            logging.info(e)

    def refresh(self, session):
        self.character = Character.refresh(session, self.character.id)
