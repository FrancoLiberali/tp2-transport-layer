import os.path
from common.safe_socket import SafeSocket

class TCPServer:
    def __init__(self, server_addr, storage_path, operations_chain):
        self.server_addr = server_addr
        self.storage_path = os.path.expandvars(storage_path)
        self.threads = []
        self.operations_chain = operations_chain

        try:
            self.sock = SafeSocket.socket()
            # The SO_REUSEADDR socket option is set in order to immediately reuse previous
            # sockets which were bound on the same address and remained in TIME_WAIT state.
            # self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.sock.bind(self.server_addr)
        except OSError as e:
            self.__close_connection()
            raise RuntimeError(f'Error iniciando Server: {str(e)}')

    def start(self):
        print(f'\nTCPServer started\nAddress: {self.server_addr}\nStorageDir: {self.storage_path})')
        self.sock.listen()

        while True:
            conn, addr = self.sock.accept()
            print(f'Connected -> address: {addr}')
            threaded_op = self.operations_chain.delegate(conn, addr, self.storage_path)
            self.threads.append(threaded_op)

    def shutdown(self):
        for thread in self.threads:
            thread.join()

        self.__close_connection()

    def __close_connection(self):
        if self.sock is not None:
            self.sock.close()
