import socket
import os.path
from tcp_server.handler import Handler

class TCPServer:
    def __init__(self, server_addr, storage_path):
        self.server_addr = server_addr
        self.storage_path = os.path.expandvars(storage_path)
        self.clients = []
        self.running = False
        self.sock = socket.socket()

        # The SO_REUSEADDR socket option is set in order to immediately reuse previous
        # sockets which were bound on the same address and remained in TIME_WAIT state.
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(self.server_addr)

    def start(self):
        print(f'TCPServer started\nAddress: {self.server_addr}\nStorageDir: {self.storage_path})')
        self.running = True
        self.sock.listen()

        while self.running:
            conn, addr = self.sock.accept()
            print(f'Connected -> address: {addr}')

            threaded_handler = Handler(conn, addr, self.storage_path)
            threaded_handler.run()
            self.clients.append((conn, addr))

    def shutdown(self):
        self.running = False

        for conn, _ in self.clients:
            conn.close()
        self.sock.close()
