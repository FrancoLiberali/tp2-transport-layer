from common.safe_socket import SafeSocket
from client.file_download import FileDownload

class TCPFileDownload(FileDownload):
    def _establish_connection(self):
        try:
            self.sock = SafeSocket.socket()
            self.sock.connect(self.server_addr)
        except OSError as e:
            self._close_connection()
            raise RuntimeError(f'Error establishing connection: {str(e)}')

    def _recv_data(self):
        return self.sock.recv()
