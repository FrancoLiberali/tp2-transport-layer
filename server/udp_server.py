from queue import Queue
from common.safe_socket import SafeSocket
from server.server import Server
from server.udp_thread_socket import UDPThreadSocket

class UDPServer(Server):
    SOCKET_TYPE = SafeSocket.UDP

    def __init__(self, server_addr, storage_path, operations_chain):
        super(UDPServer, self).__init__(server_addr, storage_path, operations_chain)
        self.queues = {}

    def start(self):
        print(f'\nUDPServer started\nAddress: {self.server_addr}\nStorageDir: {self.storage_path})')

        while True:
            data, addr = self.sock.recv()
            print(f'Recived from -> address: {addr}')
            addr_socket = self.queues.get(addr, None)
            if not addr_socket:
                addr_queue = Queue()
                conn = self.sock.accept(addr)
                addr_socket = UDPThreadSocket(conn, addr_queue)
                self.queues[addr] = addr_socket
                cli_req = data.decode()
                threaded_op = self.operations_chain.delegate(addr_socket, addr, self.storage_path, cli_req)
                threaded_op and self.threads.append(threaded_op)
            else:
                addr_socket.put(data)
