from tcp_client.file_uploader import FileUploader

def upload_file(server_address, src, name):
    fu = FileUploader(server_address, src, name)
    fu.upload()
