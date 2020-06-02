import socket
import os.path

class TCPServer:
    def __init__(self, server_addr, storage_path, operations_chain):
        self.server_addr = server_addr
        self.storage_path = os.path.expandvars(storage_path)
        self.threads = []
        self.running = False
        self.sock = socket.socket()
        self.operations_chain = operations_chain

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
            threaded_op = self.operations_chain.delegate(conn, addr, self.storage_path)
            self.threads.append(threaded_op)

    def shutdown(self):
        self.running = False
        print(f'\nShutting down gracefully...\n')

        for thread in self.threads:
            thread.join()

        self.sock.close()
