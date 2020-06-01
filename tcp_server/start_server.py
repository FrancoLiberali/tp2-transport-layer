from tcp_server.server import TCPServer


def start_server(server_address, storage_dir):
    server = TCPServer(server_address, storage_dir)

    try:
        server.start()
    except KeyboardInterrupt:
        server.shutdown()
