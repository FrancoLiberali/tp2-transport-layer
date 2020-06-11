import os
import threading
from pathlib import Path
from common.operation_codes import UPLOAD
from common.safe_socket import ConnectionBroken

class UploadOperation(threading.Thread):
    OP_CODE = UPLOAD

    def __init__(self, conn, client_addr, storage_path, file_save_name, file_size):
        super().__init__()
        self.conn = conn
        self.client_addr = client_addr
        self.storage_path = Path(storage_path)  # Path works for windows and unix delimiters
        self.file_save_name = file_save_name
        self.file_size = int(file_size)
        self.file_path = self.storage_path / self.file_save_name

    @staticmethod
    def understands(op_code):
        return op_code == UploadOperation.OP_CODE

    def run(self):
        try:
            self.conn.send(UploadOperation.OP_CODE)    # signals the client to start upload
            bytes_received = 0

            with open(self.file_path, 'wb') as f:
                while bytes_received < self.file_size:
                    chunk = self.conn.recv()
                    bytes_received += len(chunk)
                    f.write(chunk)

            print(f'SAVED FILE -> {self.file_save_name}')
            print(f'Path: {self.file_path}, {bytes_received} of {self.file_size} received.')
            self.send_end(str(bytes_received))
        except ConnectionBroken:
            os.path.isfile(self.file_path) and os.remove(self.file_path)
            print(f"Upload cancelled: cleaned up '{self.file_save_name}'")
        finally:
            self.conn.close()

    def send_end(self, bytes_received):
        try:
            self.conn.send(str(bytes_received))
        except ConnectionBroken:
            # this is the end at application level
            # i dont want to delete the uploaded file if the client lost connection at this point
            pass
