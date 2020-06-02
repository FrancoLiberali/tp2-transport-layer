class OperationsChain:
    def __init__(self, *operations):
        self.operations = operations
        self.initial_chunk = 1024   # ToDo: Implement SafeSockets and get rid of these chunks sizes

    def delegate(self, conn, client_addr, storage_path):
        init_msg = conn.recv(self.initial_chunk).decode()   # FixMe: if len(init_msg) == 0, client closed conn prematurely
        field_delimiter, fields_chunk = init_msg[0], init_msg[1:]
        fields = fields_chunk.split(field_delimiter)
        op_code, *rest = fields

        for Operation in self.operations:
            if Operation.understands(op_code):
                operation = Operation(conn, client_addr, storage_path, *rest)
                operation.start()  # Starts operation in new thread
                return operation
