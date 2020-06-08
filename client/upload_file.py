def upload_file(server_address, src, name, upload_class):
    try:
        fu = upload_class(server_address, src, name)
        fu.upload()
    except RuntimeError as e:
        print(str(e))
    except (KeyboardInterrupt, SystemExit):
        print(f"\nUpload of file '{name}' cancelled")
