import os
from abc import ABC, abstractmethod
from common.operation_codes import UPLOAD
from common.safe_socket import SafeSocket, ConnectionBroken

class FileUpload(ABC):
    def __init__(self, server_addr, src, name):
        self.OP_CODE = UPLOAD
        self.delim = '\0'
        self.file_path = os.path.expandvars(src)
        self.save_name = name
        self.file_size = self.__get_file_size()
        self.server_addr = server_addr
        self.sock = None
        self.read_chunk_size = 4096
        self._establish_connection()

    def upload(self):
        try:
            self.__send_transfer_info()
            self._wait_for_server_signal()
            self.__transfer()
            self._wait_for_server_bytes()
        except ConnectionBroken as e:
            raise RuntimeError(f'Error in connection: {str(e)}')
        finally:
            self.__close_connection()

    def __send_transfer_info(self):
        fields = [self.OP_CODE, self.save_name, self.file_size]
        fields = map(lambda field: str(field), fields)
        payload = f'{self.delim}{self.delim.join(fields)}'
        self.sock.send(payload)

    def __transfer(self):
        with open(self.file_path, 'rb') as f:
            while True:
                chunk = f.read(self.read_chunk_size)
                if not chunk:
                    break

                self.sock.send(chunk)

    def __get_file_size(self):
        try:
            return os.stat(self.file_path).st_size
        except OSError as e:
            raise RuntimeError(f'Error opening file: {str(e)}')

    def __close_connection(self):
        if self.sock is not None:
            self.sock.close()

    @abstractmethod
    def _wait_for_server_signal(self):
        pass

    @abstractmethod
    def _wait_for_server_bytes(self):
        pass

    @abstractmethod
    def _establish_connection(self):
        pass
