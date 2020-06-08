import os.path
from common.safe_socket import SafeSocket, ConnectionBroken
from server.server import Server

class TCPServer(Server):
    SOCKET_TYPE = SafeSocket.TCP

    def start(self):
        print(f'\nTCPServer started\nAddress: {self.server_addr}\nStorageDir: {self.storage_path})')
        self.sock.listen()

        while True:
            conn, addr = self.sock.accept()
            print(f'Connected -> address: {addr}')
            cli_req = self.__read_client_request(conn)  # Reads the operation the client wishes to perform
            threaded_op = self.operations_chain.delegate(conn, addr, self.storage_path, cli_req)
            threaded_op and self.threads.append(threaded_op)

    # noinspection PyMethodMayBeStatic
    def __read_client_request(self, conn):
        try:
            return conn.recv().decode()
        except ConnectionBroken:
            conn.close()
            return
