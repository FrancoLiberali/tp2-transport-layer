from common.safe_socket import SafeSocket
from client.file_upload import FileUpload

class TCPFileUpload(FileUpload):
    def _wait_for_server_signal(self):
        data = self.sock.recv().decode()
        if data != self.OP_CODE:
            raise RuntimeError('Error in protocol: OP_CODE mismatch')

    def _wait_for_server_bytes(self):
        bytes_uploaded = self.sock.recv().decode()
        print(f'Server received {bytes_uploaded} of {self.file_size} bytes successfully.')

    def _establish_connection(self):
        try:
            self.sock = SafeSocket.socket()
            self.sock.connect(self.server_addr)
        except OSError as e:
            self.__close_connection()
            raise RuntimeError(f'Error establishing connection: {str(e)}')
