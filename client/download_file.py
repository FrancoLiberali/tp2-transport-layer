def download_file(server_address, name, dst, download_class):
    try:
        fu = download_class(server_address, name, dst)
        fu.download()
    except RuntimeError as e:
        print(str(e))
    except (KeyboardInterrupt, SystemExit):
        print(f"\nDownload of file '{name}' cancelled")
