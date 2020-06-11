import os
from common.operation_codes import DOWNLOAD
from common.safe_socket import SafeSocket, ConnectionBroken
from client.file_download import FileDownload

class UDPFileDownload(FileDownload):
    def _wait_for_server_signal(self):
        data, addr = self.sock.recv()
        file_size = data.decode()
        self.file_size = int(file_size)
        if self.file_size == self.FILE_NOT_FOUND_CODE:
            raise RuntimeError(f"File '{self.name_in_server}' not found in server")

    def _transfer(self):
        bytes_received = 0

        try:
            with open(self.file_path, 'wb') as f:
                while bytes_received < self.file_size:
                    chunk, addr = self.sock.recv()
                    bytes_received += len(chunk)
                    f.write(chunk)

            print(f'Received {bytes_received} of {self.file_size} bytes successfully.')
        except ConnectionBroken:
            os.path.isfile(self.file_path) and os.remove(self.file_path)
        except FileNotFoundError as e:
            raise RuntimeError(f"Directory '{self.file_path}' not found")
        finally:
            self._close_connection()

    def _establish_connection(self):
        self.sock = SafeSocket.socket(sock_type=SafeSocket.UDP)
        self.sock.connect(self.server_addr)
