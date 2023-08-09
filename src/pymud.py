#!/usr/bin/python3
import socket
import threading
import logging
import copy

from sqlalchemy.orm import scoped_session, sessionmaker
from login_manager import LoginManager
from mud_parser import MudParser
from server_queue import ServerQueue
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
        db_session = scoped_session(
            sessionmaker(
                autoflush=True,
                bind=ENGINE
            )
        )
        logging.info(f'Connected to database at {DATABASE_ADDRESS}')
        mud_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        mud_socket.bind((host, port))
        mud_socket.listen()
        logging.info(f'Server started at {HOST}:{PORT}')

        server_queue = ServerQueue()
        unauthenticated_client_threads = []
        authenticated_client_threads = {}
        while True:
            connection, address = mud_socket.accept()
            unauthenticated_client_threads.append(ClientThread(
                connection,
                address,
                buffer_size,
                db_session,
                server_queue))
            # TODO: we don't necesarrily want to throttle any of this; it may work better on a timer
            # TODO: we can also implement a pseudo-scheduler
            for thread in copy.copy(unauthenticated_client_threads):
                if thread.character_id:
                    authenticated_client_threads.update({thread.character_id: thread})
                    unauthenticated_client_threads.remove(thread)
            with db_session() as session:
                server_queue.execute_events(session, authenticated_client_threads)


class ClientThread(threading.Thread):
    """
    Thread class to manage individual client connections
    """
    NEWLINE = b'\r\n'

    def __init__(self, connection, address, buffer_size, db_session, server_queue):
        self.connection = connection
        self.address = address
        self.buffer_size = buffer_size
        self.db_session = db_session
        self.server_queue = server_queue
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
            data = b'\r\n'
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
