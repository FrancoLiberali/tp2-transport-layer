import os
from common.operation_codes import DOWNLOAD
from common.safe_socket import SafeSocket, ConnectionBroken
from client.file_download import FileDownload

class TCPFileDownload(FileDownload):
    def _wait_for_server_signal(self):
        file_size = self.sock.recv().decode()
        self.file_size = int(file_size)
        if self.file_size == self.FILE_NOT_FOUND_CODE:
            raise RuntimeError(f"File '{self.name_in_server}' not found in server")

    def _transfer(self):
        bytes_received = 0

        try:
            with open(self.file_path, 'wb') as f:
                while bytes_received < self.file_size:
                    chunk = self.sock.recv()
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
        try:
            self.sock = SafeSocket.socket()
            self.sock.connect(self.server_addr)
        except OSError as e:
            self._close_connection()
            raise RuntimeError(f'Error establishing connection: {str(e)}')
