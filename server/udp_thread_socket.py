from queue import Empty
from common.safe_socket import ConnectionBroken, SafeSocketUDP

class UDPThreadSocket():
    def __init__(self, sock, queue, queues, recv_sock):
        self.sock = sock
        self.queue = queue
        self.queues = queues
        self.recv_sock = recv_sock

    def put(self, item):
        return self.queue.put(item)

    def send(self, data):
        return self.sock.send(data)

    def recv(self):
        try:
            return self.queue.get(timeout=SafeSocketUDP.DEFAULT_RECV_TIMEOUT)
        except Empty:
            raise ConnectionBroken("Client stoped sending")

    def close(self):
        addr = self.sock.addr
        self.queues.pop(addr)
        self.recv_sock.close_connection(addr)
        return self.sock.close()
