#!/usr/bin/python3
import socket
import threading
import logging
import copy
import sched

from sqlalchemy.orm import scoped_session, sessionmaker
from login_manager import LoginManager
from mud_parser import MudParser
from server_queue import EventQueue
from config import (HOST,
                    PORT,
                    DATABASE_ADDRESS,
                    BUFFER_SIZE,
                    ENGINE)

class MudServer:
    """
    Container for all server child threads
    """
    engine = ENGINE
    def __init__(self, host, port, buffer_size):
        self.db_session = scoped_session(
            sessionmaker(
                autoflush=True,
                bind=ENGINE
            )
        )
        logging.info(f'Connected to database at {DATABASE_ADDRESS}')
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((host, port))
        self.socket.listen()
        logging.info(f'Server started at {HOST}:{PORT}')

        self.buffer_size = buffer_size
        self.event_queue = EventQueue()
        self.unauthenticated_client_threads = []
        self.authenticated_client_threads = {}
        self.scheduler = sched.scheduler()

        self.scheduler.enter(1, 1, self._accept_connections)
        self.scheduler.enter(2, 2, self._refresh_threads)
        self.scheduler.run()

    def _accept_connections(self):
        """
        Accept incoming connections and append to list
        """
        connection, address = self.socket.accept()
        self.unauthenticated_client_threads.append(ClientThread(
            connection,
            address,
            self.buffer_size,
            self.db_session,
            self.event_queue))

    def _refresh_threads(self):
        """
        Mark newly authenticated threads and remove old threads
        """
        for thread in copy.copy(self.unauthenticated_client_threads):
            if thread.character_id:
                self.authenticated_client_threads.update({thread.character_id: thread})
                self.unauthenticated_client_threads.remove(thread)
        for character_id, thread in copy.copy(self.authenticated_client_threads).items():
            if not thread.is_alive():
                self.authenticated_client_threads.pop(character_id)
            
        with self.db_session() as session:
            self.event_queue.execute_events(session, self.authenticated_client_threads)


class ClientThread(threading.Thread):
    """
    Thread class to manage individual client connections
    """
    NEWLINE = b'\r\n'

    def __init__(self, connection, address, buffer_size, db_session, event_queue):
        self.connection = connection
        self.address = address
        self.buffer_size = buffer_size
        self.db_session = db_session
        self.server_queue = event_queue
        self.character_id = None

        super().__init__()
        self.start()

    def run(self):
        logging.info(f'Client connected: {self.address}')
        # TODO: send json on first message upon front-end connection
        # data = self.connection.recv(self.buffer_size)
        data = b'{"character_name": "Rha", "account_hash": "1"}'
        with self.db_session() as session:
            login_manager = LoginManager(session, data, self.address, self.send_message)
            self.character_id = login_manager.character.id

        if login_manager.success:
            data = b'look\r\n'
            while data:
                logging.info(data)
                if data.strip():
                    with self.db_session() as session:
                        login_manager.refresh(session)
                        response = MudParser.parse_data(session, login_manager.character, data)
                    self.send_message(response)
                data = self.connection.recv(self.buffer_size)
        self.connection.close()
        logging.info(f'Client disconnected: {self.address}')

    def send_message(self, message: str):
        self.connection.send(message + self.NEWLINE)

if __name__ == '__main__':
    MudServer(HOST, PORT, BUFFER_SIZE)
