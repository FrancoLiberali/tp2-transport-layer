import os
from abc import ABC, abstractmethod
from common.operation_codes import DOWNLOAD
from common.safe_socket import SafeSocket, ConnectionBroken

class FileDownload(ABC):
    FILE_NOT_FOUND_CODE = -1

    def __init__(self, server_addr, file_name, dest):
        self.OP_CODE = DOWNLOAD
        self.delim = '\0'
        self.file_path = dest
        self.name_in_server = file_name
        self.server_addr = server_addr
        self.sock = None
        self._establish_connection()
        self.file_size = None

    def download(self):
        try:
            self.__send_transfer_info()
            self.__wait_for_server_signal()
            self.__transfer()
        except ConnectionBroken as e:
            raise RuntimeError(f'Error in connection: {str(e)}')
        finally:
            self._close_connection()

    def __send_transfer_info(self):
        fields = [self.OP_CODE, self.name_in_server]
        payload = f'{self.delim}{self.delim.join(fields)}'
        self.sock.send(payload)

    def __wait_for_server_signal(self):
        file_size = self._recv_data().decode()
        self.file_size = int(file_size)
        if self.file_size == self.FILE_NOT_FOUND_CODE:
            raise RuntimeError(f"File '{self.name_in_server}' not found in server")

    def __transfer(self):
        bytes_received = 0

        try:
            with open(self.file_path, 'wb') as f:
                while bytes_received < self.file_size:
                    chunk = self._recv_data()
                    bytes_received += len(chunk)
                    f.write(chunk)

            print(f'Received {bytes_received} of {self.file_size} bytes successfully.')
        except ConnectionBroken:
            os.path.isfile(self.file_path) and os.remove(self.file_path)
        except FileNotFoundError as e:
            raise RuntimeError(f"Directory '{self.file_path}' not found")
        finally:
            self._close_connection()

    def _close_connection(self):
        if self.sock is not None:
            self.sock.close()

    @abstractmethod
    def _establish_connection(self):
        pass

    @abstractmethod
    def _recv_data(self):
        pass
