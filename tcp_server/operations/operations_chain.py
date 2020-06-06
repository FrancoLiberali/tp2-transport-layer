from common.safe_socket import ConnectionBroken

class OperationsChain:
    def __init__(self, *operations):
        self.operations = operations

    def delegate(self, conn, client_addr, storage_path):
        try:
            init_msg = conn.recv().decode()
        except ConnectionBroken:
            conn.close()
            return

        field_delimiter, fields_chunk = init_msg[0], init_msg[1:]
        fields = fields_chunk.split(field_delimiter)
        op_code, *rest = fields

        for Operation in self.operations:
            if Operation.understands(op_code):
                operation = Operation(conn, client_addr, storage_path, *rest)
                operation.start()  # Starts operation in new thread
                return operation
