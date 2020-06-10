from abc import ABC, abstractmethod
import socket

def _get_max_representable_number(number_of_bytes, byteorder='little'):
    max_number = int(-1).to_bytes(number_of_bytes, byteorder=byteorder, signed=True)
    return int.from_bytes(max_number, byteorder=byteorder, signed=False)

class SafeSocket(ABC):
    TCP = socket.SOCK_STREAM
    UDP = socket.SOCK_DGRAM
    MSG_LEN_REPR_BYTES = 2    # number of bytes used to represent the length of a message
    MAX_MSG_LEN = _get_max_representable_number(MSG_LEN_REPR_BYTES)
    DEFAULT_READ_BUFF = 2048

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

    def send(self, data):
        data = self._as_bytes(data)
        datalength = len(data)
        data = self._make_header(datalength) + data  # concatenate msg header to start of data
        datalength = len(data)  # update length with added bytes

        bytes_sent = self._send_safe(datalength, data)
        self._recv_ack(datalength, data)
        return bytes_sent

    def _send_safe(self, datalength, data):
        total_bytes_sent = 0
        while total_bytes_sent < datalength:
            bytes_sent = self._sock_send(data[total_bytes_sent:])
            total_bytes_sent += bytes_sent
            self._check_conn(bytes_sent)
        return total_bytes_sent

    def close(self):
        self.sock.close()

    def _make_socket(self, sock=None):
        return self._make_underlying_socket() if sock is None else self._wrap_socket(sock)

    def _wrap_socket(self, sock):
        safe_sock = self.__class__()    # Create new instance of child class
        safe_sock.sock = sock       # Set it's underlying socket
        return safe_sock

    # noinspection PyMethodMayBeStatic
    def _check_conn(self, bytes_handled):
        if bytes_handled == 0:
            raise ConnectionBroken('Connection closed by peer')

    # noinspection PyMethodMayBeStatic
    def _as_bytes(self, data):
        if isinstance(data, bytes):
            pass
        elif isinstance(data, str):
            data = data.encode()
        else:
            raise TypeError('Data must be bytes or str')

        if len(data) > self.MAX_MSG_LEN:
            raise ValueError(f'Data must be at most {self.MAX_MSG_LEN} bytes. Consider splitting into chunks.')

        return data

    # noinspection PyMethodMayBeStatic
    def _encode_length(self, datalength):
        return self._encode_as_bytes(datalength, self.MSG_LEN_REPR_BYTES)

    def _encode_as_bytes(self, data, size):
        return data.to_bytes(size, byteorder='little', signed=False)

    # noinspection PyMethodMayBeStatic
    def _decode_bytes(self, lengthdata):
        return int.from_bytes(lengthdata, byteorder='little', signed=False)

    @abstractmethod
    def _make_underlying_socket(self):
        pass

    @abstractmethod
    def _sock_send(self, data):
        pass

    @abstractmethod
    def recv(self):
        pass

    @abstractmethod
    def _recv_ack(self, datalength, data):
        pass

class SafeSocketTCP(SafeSocket):
    def _make_underlying_socket(self):
        return socket.socket(type=self.TCP)

    def connect(self, address):
        self.sock.connect(address)

    def listen(self):
        self.sock.listen()

    def accept(self):
        conn, addr = self.sock.accept()
        safe_conn = self._make_socket(sock=conn)
        safe_conn.sock = conn
        return safe_conn, addr

    def _sock_send(self, data):
        return self.sock.send(data)

    def recv(self):
        datalength = self.__read_safely(self.MSG_LEN_REPR_BYTES)   # Reads first 2 bytes with length of message
        datalength = self._decode_bytes(datalength)
        return self.__read_safely(datalength)

    def __read_safely(self, length):
        chunks = []
        total_bytes_recvd = 0

        while total_bytes_recvd < length:
            bufsize = min(length - total_bytes_recvd, self.DEFAULT_READ_BUFF)
            chunk = self.sock.recv(bufsize)
            self._check_conn(len(chunk))
            chunks.append(chunk)
            total_bytes_recvd += len(chunk)

        return b''.join(chunks)

    def _make_header(self, datalength):
        return self._encode_length(datalength) # concatenate msg length to start of data

    def _recv_ack(self, datalength, data):
        pass

class SafeSocketUDP(SafeSocket):
    SEQ_NUM_OFFSET = 2
    SEQ_NUM_MASK = 1 << SEQ_NUM_OFFSET
    IS_ACK_OFFSET = 1
    IS_ACK_MASK = 1 << IS_ACK_OFFSET
    ACK_SEQ_NUM_OFFSET = 0
    ACK_SEQ_NUM_MASK = 1 << ACK_SEQ_NUM_OFFSET
    #                     flags byte
    # ------------------------------------------------------
    # | 0 | 0 | 0 | 0 | 0 | seq_num | is_ack | ack_seq_num |
    # ------------------------------------------------------
    # | 7 | 6 | 5 | 4 | 3 |    2    |   1    |      0      | [bits]

    FLAGS_POS = 0
    FLAGS_SIZE = 1
    MSG_LEN_POS = 1
    HEADER_SIZE = FLAGS_SIZE + SafeSocket.MSG_LEN_REPR_BYTES
    #             header
    # -----------------------------
    # | flags |      msg_len      |
    # -----------------------------
    # |   0   |    1    |    2    | [bytes]
    MAX_RETRANSMITIONS = 25
    RTO = 0.250
    DEFAULT_RECV_TIMEOUT = 10

    def __init__(self):
        super().__init__()
        self.addr = None
        self.seq_num = 0
        self.last_acked = {}

    def _make_header(self, datalength, is_ack=0, ack_seq_num = 0):
        flags = self._encode_as_bytes(self.seq_num << self.SEQ_NUM_OFFSET | is_ack << self.IS_ACK_OFFSET | ack_seq_num << self.ACK_SEQ_NUM_OFFSET, self.FLAGS_SIZE)
        datalength = self._encode_length(datalength)
        return flags + datalength

    def _make_underlying_socket(self):
        return socket.socket(type=self.UDP)

    # noinspection PyMethodMayBeStatic
    def accept(self, addr):
        safe_conn = SafeSocket.socket(sock_type=SafeSocket.UDP)
        safe_conn.addr = addr
        return safe_conn

    def connect(self, addr):
        self.addr = addr

    def _sock_send(self, data):
        return self.sock.sendto(data, self.addr)

    def recv(self, timeout = DEFAULT_RECV_TIMEOUT):
        try:
            self.sock.settimeout(timeout)
            flags, datalength, addr = self.__recv_header(socket.MSG_PEEK)
            # Read all the datagram, including the bytes from header
            data, addr = self.__read_safely(self.HEADER_SIZE + datalength)
            seq_num = self.__get_seq_num(flags)
            last_acked = self.__get_last_acked(addr)
            # if it is a new datagram
            if seq_num != last_acked:
                self.sock.settimeout(None)
                self.__send_ack(addr, seq_num)
                # Return the data of the datagram
                return data[self.HEADER_SIZE:], addr
            # it is a retransmition, my last ack went lost
            # send the last_acked again and wait until receiving the correct datagram
            self.__send_ack(addr, last_acked)
            return self.recv()
        except socket.timeout:
            raise ConnectionBroken('Client stoped sending')

    def close_connection(self, addr):
        self.last_acked.pop(addr, None)

    def __get_last_acked(self, addr):
        return self.last_acked.get(addr, None)

    def __recv_header(self, *flags):
        # Reads header of message
        header, addr = self.__read_safely(self.HEADER_SIZE, *flags)
        flags = self._decode_bytes(header[self.FLAGS_POS:self.FLAGS_POS + self.FLAGS_SIZE + 1])
        datalength = self._decode_bytes(header[self.MSG_LEN_POS:])
        return flags, datalength, addr

    def _recv_ack(self, datalength, data):
        for i in range(self.MAX_RETRANSMITIONS):
            self.sock.settimeout(self.RTO)
            try:
                flags, datalength, addr = self.__recv_header()
                is_ack = self.__get_is_ack(flags)
                ack_seq_num = self.__get_ack_seq_num(flags)
                # this make the channel half duplex, i can't receive until i get an ack
                if is_ack and ack_seq_num == self.seq_num:
                    self.seq_num = 1 - self.seq_num
                    self.sock.settimeout(None)
                    return
            except socket.timeout:
                # retransmition
                self._send_safe(datalength, data)
        raise ConnectionBroken('Destiny not receiving datagrams')

    def __send_ack(self, addr, seq_num):
        header = self._make_header(0, 1, seq_num)
        self.sock.sendto(header, addr)
        self.last_acked[addr] = seq_num

    def __get_seq_num(self, flags):
        return (flags & self.SEQ_NUM_MASK) >> self.SEQ_NUM_OFFSET

    def __get_is_ack(self, flags):
        return (flags & self.IS_ACK_MASK) >> self.IS_ACK_OFFSET

    def __get_ack_seq_num(self, flags):
        return (flags & self.ACK_SEQ_NUM_MASK) >> self.ACK_SEQ_NUM_OFFSET

    def __read_safely(self, length, *flags):
        chunks = []
        total_bytes_recvd = 0
        addr = None
        while total_bytes_recvd < length:
            chunk, addr = self.sock.recvfrom(length, socket.MSG_PEEK)
            # the socket is not expecting to receive from someone in particular
            # or received from the ip expected ([0] to not take in count the port from which the answer came from)
            if not self.addr or self.addr[0] == addr[0]:
                chunks.append(chunk)
                total_bytes_recvd += len(chunk)
            else:
                # remove datagram from the udp buffer
                self.sock.recvfrom(1)
        # remove datagram from the udp buffer unless flags have MSG_PEEK
        self.sock.recvfrom(1, *flags)
        return b''.join(chunks), addr

class ConnectionBroken(RuntimeError):
    pass
