#!/usr/bin/python3
import socket
import threading
import logging

HOST = '0.0.0.0' 
PORT = 5000
BUFFER_SIZE = 1024

logging.basicConfig(
    format='%(asctime)s %(levelname)-8s %(message)s',
    level=logging.DEBUG,
    datefmt='%Y-%m-%d %H:%M:%S'
)

class MudServer:
    def __init__(self, host, port, buffer_size):
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
        data = self.connection.recv(self.buffer_size)

        while data:
            self.connection.send(data)
            data = self.connection.recv(self.buffer_size)
        self.connection.close()
        logging.info(f'Client disconnected: {self.address}')

if __name__ == '__main__':
    MudServer(HOST, PORT, BUFFER_SIZE)
