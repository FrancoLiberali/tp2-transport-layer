class UDPThreadSocket():
    def __init__(self, sock, queue):
        self.sock = sock
        self.queue = queue

    def put(self, item):
        return self.queue.put(item)

    def send(self, data):
        return self.sock.send(data)

    def recv(self):
        return self.queue.get()

    def close(self):
        return self.sock.close()
