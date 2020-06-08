from common.safe_socket import SafeSocket
from client.file_upload import FileUpload

class UDPFileUpload(FileUpload):
    def _wait_for_server_signal(self):
        data, addr = self.sock.recv()
        data = data.decode()
        if data != self.OP_CODE:
            raise RuntimeError('Error in protocol: OP_CODE mismatch')

    def _wait_for_server_bytes(self):
        bytes_uploaded, addr = self.sock.recv()
        bytes_uploaded = bytes_uploaded.decode()
        print(f'Server received {bytes_uploaded} of {self.file_size} bytes successfully.')

    def _establish_connection(self):
        self.sock = SafeSocket.socket(sock_type=SafeSocket.UDP)
        self.sock.connect(self.server_addr)
