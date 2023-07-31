import json
import logging

from data.models import Character
from exceptions import LoginError

class LoginManager:
    def __init__(self, data, connection, address):
        self.success = False
        login_info = json.loads(data)

        try:
            if Character.validate_account(login_info['character_name'], login_info['account_hash']):
                connection.send(f'Welcome {login_info["character_name"]}!\r\n'.encode('utf-8'))
                logging.info(f'{login_info["character_name"]} succesfully authenticated - {address}')
                self.character_name = login_info["character_name"]
                self.success = True
            else:
                connection.send(f'Invalid login credentials!\r\n'.encode('utf-8'))
                logging.info(f'Invalid login: {login_info["character_name"]} - {address}')
        except LoginError as e:
            connection.send(f'No character found by the name of {login_info["character_name"]}!\r\n'.encode('utf-8'))
            logging.info(e)
