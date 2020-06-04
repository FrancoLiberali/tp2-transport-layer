from abc import ABC, abstractmethod
import socket

class SafeSocket(ABC):
    TCP = socket.SOCK_STREAM
    UDP = socket.SOCK_DGRAM

    def __init__(self):
        self.sock = self._make_socket()
        # The SO_REUSEADDR socket option is set in order to immediately reuse previous
        # sockets which were bound on the same address and remained in TIME_WAIT state.
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    @staticmethod
    def socket(sock_type=TCP):
        return SafeSocketUDP() if sock_type == SafeSocket.UDP else SafeSocketTCP()

    def bind(self, address):
        self.sock.bind(address)

    def connect(self, address):
        self.sock.connect(address)

    def listen(self):
        self.sock.listen()

    def accept(self):
        conn, addr = self.sock.accept()
        safe_conn = self._make_socket(sock=conn)
        safe_conn.sock = conn
        return safe_conn, addr

    def close(self):
        self.sock.close()

    def _make_socket(self, sock=None):
        return self._make_underlying_socket() if sock is None else self._wrap_socket(sock)

    def _wrap_socket(self, sock):
        safe_sock = self.__class__()    # Create new instance of child class
        safe_sock.sock = sock       # Set it's underlying socket
        return safe_sock

    @abstractmethod
    def _make_underlying_socket(self):
        pass

    @abstractmethod
    def send(self, data):
        pass

    @abstractmethod
    def recv(self):
        pass

class SafeSocketTCP(SafeSocket):

    def _make_underlying_socket(self):
        return socket.socket(type=self.TCP)

    def send(self, data):
        return self.sock.send(data)     # FixMe: actually make this SAFE

    def recv(self):
        chunk = 4096    # FixMe: actually make this SAFE
        return self.sock.recv(chunk)

class SafeSocketUDP(SafeSocket):

    def _make_underlying_socket(self):
        return socket.socket(type=self.UDP)

    def send(self, data):
        raise NotImplementedError('UDP SafeSocket not implemented')

    def recv(self):
        raise NotImplementedError('UDP SafeSocket not implemented')
