import os
import threading
from pathlib import Path
from common.operation_codes import DOWNLOAD
from common.safe_socket import ConnectionBroken

class DownloadOperation(threading.Thread):
    OP_CODE = DOWNLOAD

    def __init__(self, conn, client_addr, storage_path, file_name):
        super().__init__()
        self.conn = conn
        self.client_addr = client_addr
        self.storage_path = Path(storage_path)  # Path works for windows and unix delimiters
        self.file_name = file_name
        self.file_path = self.storage_path / self.file_name
        self.file_size = self.__get_file_size()
        self.read_chunk_size = 4096

    @staticmethod
    def understands(op_code):
        return op_code == DownloadOperation.OP_CODE

    def run(self):
        try:
            self.conn.send(str(self.file_size))     # sends file size to client to start downloading
            bytes_sent = 0

            with open(self.file_path, 'rb') as f:
                while bytes_sent < self.file_size:
                    chunk = f.read(self.read_chunk_size)
                    self.conn.send(chunk)
                    bytes_sent += len(chunk)

        except ConnectionBroken:
            print(f"Download cancelled: '{self.file_name}'")
        finally:
            self.conn.close()

    def __get_file_size(self):
        try:
            return os.stat(self.file_path).st_size
        except OSError as e:
            raise RuntimeError(f'Error opening file: {str(e)}')
