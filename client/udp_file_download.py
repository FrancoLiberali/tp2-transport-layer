from common.safe_socket import SafeSocket
from client.file_download import FileDownload

class UDPFileDownload(FileDownload):
    def _establish_connection(self):
        self.sock = SafeSocket.socket(sock_type=SafeSocket.UDP)
        self.sock.connect(self.server_addr)

    def _recv_data(self):
        return self.sock.recv()[0]
