import threading

class Handler(threading.Thread):
    def __init__(self, conn, addr, storage_path):
        super().__init__()
        self.conn = conn
        self.addr = addr
        self.storage_path = storage_path
        self.delim = '\0'

    def run(self):
        init_msg = self.conn.recv(1024).decode()
        operation, file_name, file_size, chunk_size = init_msg.split(self.delim)
        file_size, chunk_size = int(file_size), int(chunk_size)
        dst_path = f'{self.storage_path}/{file_name}'
        bytes_received = 0
        self.conn.send(operation.encode())  # Tell client to begin upload

        with open(dst_path, 'wb') as f:
            while bytes_received < file_size:
                chunk = self.conn.recv(chunk_size)
                bytes_received += len(chunk)
                f.write(chunk)

            self.conn.send(str(bytes_received).encode())
            self.conn.close()

        print(f'Saved file: {self.storage_path}/{file_name}')
