import os.path
from abc import ABC, abstractmethod

from common.safe_socket import SafeSocket, ConnectionBroken

class Server(ABC):
    def __init__(self, server_addr, storage_path, operations_chain):
        self.server_addr = server_addr
        self.storage_path = os.path.expandvars(storage_path)
        self.threads = []
        self.operations_chain = operations_chain

        try:
            self.sock = SafeSocket.socket(sock_type=self.__class__.SOCKET_TYPE)
            self.sock.bind(self.server_addr)
        except OSError as e:
            self.__close_connection()
            raise RuntimeError(f'Error initializing server: {str(e)}')

    @abstractmethod
    def start(self):
        pass

    def shutdown(self):
        for thread in self.threads:
            thread.join()

        self.__close_connection()

    def __close_connection(self):
        if self.sock is not None:
            self.sock.close()
