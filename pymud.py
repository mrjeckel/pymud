#!/usr/bin/python3
import socket
import threading

HOST = '127.0.0.1' 
PORT = 5000
BUFFER_SIZE = 1024

class MudServer:
    def __init__(self, host, port, buffer_size):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.bind((host, port))
        self.socket.listen()

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
        data = self.connection.recv(self.buffer_size)

        while data:
            self.connection.send(data)
            data = self.connection.recv(self.buffer_size)
        self.connection.close()

if __name__ == '__main__':
    MudServer(HOST, PORT, BUFFER_SIZE)
