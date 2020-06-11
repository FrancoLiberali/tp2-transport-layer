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
            self._wait_for_server_signal()
            self._transfer()
        except ConnectionBroken as e:
            raise RuntimeError(f'Error in connection: {str(e)}')
        finally:
            self._close_connection()

    def __send_transfer_info(self):
        fields = [self.OP_CODE, self.name_in_server]
        payload = f'{self.delim}{self.delim.join(fields)}'
        self.sock.send(payload)

    def _close_connection(self):
        if self.sock is not None:
            self.sock.close()

    @abstractmethod
    def _wait_for_server_signal(self):
        pass

    @abstractmethod
    def _transfer(self):
        pass

    @abstractmethod
    def _establish_connection(self):
        pass
