from tcp_client.file_upload import FileUpload

def upload_file(server_address, src, name):
    try:
        fu = FileUpload(server_address, src, name)
        fu.upload()
    except RuntimeError as e:
        print(str(e))
    except (KeyboardInterrupt, SystemExit):
        print(f"\nUpload of file '{name}' cancelled")
