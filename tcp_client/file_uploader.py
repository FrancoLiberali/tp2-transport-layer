import socket
import os

class FileUploader:
    def __init__(self, server_addr, src, name):
        self.OP_CODE = 'upload'
        self.delim = '\0'
        self.chunk_size = 4096
        self.file_path = os.path.expandvars(src)
        self.save_name = name
        self.file_size = os.stat(self.file_path).st_size
        self.server_addr = server_addr
        self.sock = socket.socket()
        self.sock.connect(self.server_addr)

    def upload(self):
        self.__send_transfer_info()
        with open(self.file_path, 'rb') as f:
            while True:
                chunk = f.read(self.chunk_size)

                if not chunk:
                    break

                self.sock.send(chunk)

        bytes_uploaded = self.sock.recv(self.chunk_size).decode()
        print(f'Server received {bytes_uploaded} of {self.file_size} bytes successfully.')
        self.sock.close()

    def __send_transfer_info(self):
        fields = map(lambda field: str(field), [self.OP_CODE, self.save_name, self.file_size, self.chunk_size])
        payload = f'{self.delim}{self.delim.join(fields)}'
        self.__transfer(payload)
        self.__wait_for_server()

    def __transfer(self, payload):
        sent = self.sock.send(payload.encode())
        if sent != len(payload):
            raise ValueError('Conexión rota')

    def __wait_for_server(self):
        data = self.sock.recv(self.chunk_size).decode()
        if data != self.OP_CODE:
            raise ValueError('La bardeó el server')

