from tcp_server.server import TCPServer
from tcp_server.operations.upload_operation import UploadOperation
from tcp_server.operations.operations_chain import OperationsChain


def start_server(server_address, storage_dir):
    chain = OperationsChain(UploadOperation)
    server = TCPServer(server_address, storage_dir, chain)

    try:
        server.start()
    except (KeyboardInterrupt, SystemExit):
        server.shutdown()
