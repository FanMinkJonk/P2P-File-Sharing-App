import peer.peer_be as peer
import cmd

class Peer_vt(cmd.Cmd):
    intro = "Welcome to the virtual terminal! Type 'help' to see a list of commands."
    prompt = "peer> "
    
    def __init__(self, mode):
        super().__init__()
        assert isinstance(mode, peer.Peer)
        self._peer = mode
     
    def do_help(self, arg):
        args = arg.split()
        print()
        if len(args) == 0:
            commands = {
                "connect": "connect to a tracker.",
                "exit": "exit terminal.",
                "list_peers": "display a list of connected peers.",
                "ping <peer_index>": "ping to a specific ip address.",
                "download <filename> <author-ip>": "download a specified file.",
                "upload <filename>": "upload a specified file.",
                # "download_torrent <file_name> <ip>": "download a file using torrent (metadata required).",
                # "create_torrent <file_name> <piece_size>": "create torrent metadata for a file.",
                # "download_magnet <magnet_link> <seed_ip>": "download a file using magnet text.",
                # "magnet_text <magnet_text> <tracker_url> <seed_ip>": "fetch metadata from tracker and download file using magnet text.",
                "help <command>": "display the command syntax."
            }
            print("~~ Help menu ~~")
            for cmd, desc in commands.items():
                print(f"  {cmd:40} - {desc}")
        elif arg == "connect":
            print("connect --server-ip <ip> --server-port <port>")
        elif arg == "exit":
            print("exit")
        elif arg == "list_peers":
            print("list_peers")
        elif arg == "ping":
            print("ping --client-ip --client-port")
        elif arg == "download":
            print("download --destination-folder --filename --author-ip")        
        elif arg == "upload":
            print("upload --filename")
        else:
            print("Usage: help or help <command>")
        print()
    
    def do_connect(self, arg):
        args = arg.split()
        print()
        if len(args) == 2:
            server_ip = args[0]
            server_port = int(args[1])

            try:
                print("Connecting to tracker")
                self._peer.connect_server(server_ip, server_port)
                print("Tracker connected")
            except Exception as e:
                print(f"Error connecting to tracker:{e}")
        else:
            print("Usage: connect <server ip> <server port>")
            return
        print()

    def do_exit(self, arg):
        args = arg.split()
        print()
        if len(args) == 0:
            try:
                print("Exiting...")
                self._peer.exit()
            except Exception as e:
                print(f"Error while exiting: {e}")
            return True
        else:
            print("This command doesn't require any arguments !!!")
        print()
    
    def do_list_peers(self, arg):
        args = arg.split()
        print()
        if len(args) == 0:
            try:
                if self._peer.is_connected:
                    print("Retreiving connected peers")
                    print()
                    
                    list_peers, list_peers_files = self._peer.get_list_peers()

                    if len(list_peers) == 0:
                        print("There are no peer connected to that tracker!!!")
                    else:
                        print("Peer list:")
                        for i in range(len(list_peers)):
                            print(i+1, list_peers[i][0], ":", list_peers[i][1])
                            for p in list_peers_files:
                                if p["author"][0] == list_peers[i][0] and p["author"][1] == list_peers[i][1]:
                                    print(f"  - File name: {p['file name']}, file size: {p['file size']}KB")
                else:
                    print("This peer is not connected to any tracker")
            except Exception as e:
                print(f"Error retreiving connected peers list: {e}")
        else:
            print("This command doesn't require any arguments !!!")
        print()
    
    def do_ping(self, arg):
        args = arg.split()
        print()
        if len(args) == 1:
            try:
                list_peers, list_peers_files = self._peer.get_list_peers()
                if not self._peer.is_connected:
                    print("This peer is not currently connected to any tracker!!!")
                elif len(list_peers) == 0:
                    print("There are no peer connected to this tracker!!!")
                else:
                    check = self._peer.ping(int(args[0])-1)
                    if check:
                        print(f"Succesfully ping to {list_peers[int(args[0])-1][0]}:{list_peers[int(args[0])-1][1]}")
                    else:
                        print(f"Failed to ping to {list_peers[int(args[0])-1][0]}:{list_peers[int(args[0])-1][1]}")
                    self._peer._peer_ping_check = 0
            except peer.PeerNotFound:
                print("Peer not found, invalid index!!!")
            except Exception as e:
                print("Error while ping to peer: ",e)
        else:
            print("Usage: ping <peer-index>")
        print()
    
    def do_download(self, arg):
        args = arg.split()
        print()
        if len(args) != 2:
            print("Usage: download <filename> <author-ip>")
        else:
            filename, author_ip = args
            destination_folder = "downloaded_files"  # Use only one folder here
            author_port = 22237  # Fixed port for file transfers

            try:
                file_path = self._peer.download_file(author_ip, author_port, filename, destination_folder)
                print(f"Downloaded file saved at: {file_path}")
            except Exception as e:
                print(f"Error during file download:{e}")
        print()
    
    def do_upload(self, arg):
        args = arg.split()
        if len(args) != 1:
            print("Usage: upload <filepath>")
        else:

            # Get the file path from input argument
            filepath = args[0]
            destination_folder = "shared_files"  # Folder where the upload server serves files
            
            print()
            try:
                if self._peer.upload(filepath, destination_folder):
                    print(f"File '{filepath}' uploaded successfully to '{destination_folder}'.")
                else:
                    print(f"File '{filepath}' has already been uploaded to tracker!")
            except Exception as e:
                print("Error during file upload:", e)
        print()
