#!/usr/bin/python3
import socket
import threading
import logging

from login_manager import LoginManager
from mud_parser import MudParser
from config import (HOST,
                    PORT,
                    DATABASE_ADDRESS,
                    BUFFER_SIZE,
                    ENGINE)

class MudServer:
    engine = ENGINE
    def __init__(self, host, port, buffer_size):
        logging.info(f'Connected to database at {DATABASE_ADDRESS}')
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((host, port))
        self.socket.listen()
        logging.info(f'Server started at {HOST}:{PORT}')

        while True:
            connection, address = self.socket.accept()
            MudThread(connection, address, buffer_size)

class MudThread(threading.Thread):
    def __init__(self, connection, address, buffer_size):
        self.connection = connection
        self.address = address
        self.buffer_size = buffer_size

        super().__init__()
        self.start()

    def run(self):
        logging.info(f'Client connected: {self.address}')
        # TODO: send json on first message upon front-end connection
        # data = self.connection.recv(self.buffer_size)
        data = b'{"character_name": "Rha", "account_hash": "1"}'
        login_manager = LoginManager(data, self.connection, self.address)

        data = self.connection.recv(self.buffer_size)

        if login_manager.success:
            while data:
                response = MudParser.parse_data(data, login_manager.character_name)
                self.connection.send(response)
                data = self.connection.recv(self.buffer_size)
        self.connection.close()
        logging.info(f'Client disconnected: {self.address}')

if __name__ == '__main__':
    MudServer(HOST, PORT, BUFFER_SIZE)
