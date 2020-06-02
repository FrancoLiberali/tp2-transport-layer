import threading
from common.operations import UPLOAD

class UploadOperation(threading.Thread):
    OP_CODE = UPLOAD

    def __init__(self, conn, client_addr, storage_path, file_save_name, file_size, chunk_size):
        super().__init__()
        self.conn = conn
        self.client_addr = client_addr
        self.storage_path = storage_path
        self.file_save_name = file_save_name
        self.file_size = int(file_size)
        self.chunk_size = int(chunk_size)

    @staticmethod
    def understands(op_code):
        return op_code == UploadOperation.OP_CODE

    def run(self):
        self.conn.send(UploadOperation.OP_CODE.encode())    # signals the client to start upload
        path = f'{self.storage_path}/{self.file_save_name}'
        bytes_received = 0

        with open(path, 'wb') as f:
            while bytes_received < self.file_size:
                chunk = self.conn.recv(self.chunk_size)

                if len(chunk) == 0:     # Conn was closed by client prematurely
                    break

                bytes_received += len(chunk)
                f.write(chunk)

        print(f'SAVED FILE -> {self.file_save_name}')
        print(f'Path: {path}, {bytes_received} of {self.file_size} received.')
        self.conn.send(str(bytes_received).encode())
        self.conn.close()

