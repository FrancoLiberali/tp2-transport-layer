class OperationsChain:
    def __init__(self, *operations):
        self.operations = operations

    def delegate(self, conn, client_addr, storage_path, cli_req):
        if cli_req is None:
            return

        field_delimiter, fields_chunk = cli_req[0], cli_req[1:]
        fields = fields_chunk.split(field_delimiter)
        op_code, *rest = fields

        for Operation in self.operations:
            if Operation.understands(op_code):
                operation = Operation(conn, client_addr, storage_path, *rest)
                operation.start()  # Starts operation in new thread
                return operation
