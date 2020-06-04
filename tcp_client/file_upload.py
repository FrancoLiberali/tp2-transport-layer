import os
from common.operations import UPLOAD
from common.safe_socket import SafeSocket

class FileUpload:
    def __init__(self, server_addr, src, name):
        self.OP_CODE = UPLOAD
        self.delim = '\0'
        self.chunk_size = 4096
        self.file_path = os.path.expandvars(src)
        self.save_name = name
        self.file_size = self.__get_file_size()
        self.server_addr = server_addr
        self.sock = None
        self.__establish_connection()

    def upload(self):
        try:
            self.__send_transfer_info()
            self.__wait_for_server_signal()
            self.__transfer()
            self.__wait_for_server_bytes()
        except OSError as e:
            raise RuntimeError(f'Error en la conexión: {str(e)}')
        finally:
            self.__close_connection()

    def __send_transfer_info(self):
        fields = [self.OP_CODE, self.save_name, self.file_size, self.chunk_size]    # ToDo: remove chunk_size, let SafeSocket handle it
        fields = map(lambda field: str(field), fields)
        payload = f'{self.delim}{self.delim.join(fields)}'
        self.sock.send(payload.encode())

    def __wait_for_server_signal(self):
        data = self.sock.recv().decode()
        if data != self.OP_CODE:
            raise RuntimeError('Error de protocolo: OP_CODE mismatch')

    def __transfer(self):
        with open(self.file_path, 'rb') as f:
            while True:
                chunk = f.read(self.chunk_size)
                if not chunk:
                    break

                self.sock.send(chunk)

    def __wait_for_server_bytes(self):
        bytes_uploaded = self.sock.recv().decode()
        print(f'Server received {bytes_uploaded} of {self.file_size} bytes successfully.')

    def __get_file_size(self):
        try:
            return os.stat(self.file_path).st_size
        except OSError as e:
            raise RuntimeError(f'Error abriendo archivo: {str(e)}')

    def __establish_connection(self):
        try:
            self.sock = SafeSocket.socket()
            self.sock.connect(self.server_addr)
        except OSError as e:
            self.__close_connection()
            raise RuntimeError(f'Error estableciendo conexión: {str(e)}')

    def __close_connection(self):
        if self.sock is not None:
            self.sock.close()
