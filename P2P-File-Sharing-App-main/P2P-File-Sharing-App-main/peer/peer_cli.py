import peer.peer_be as peer
import cmd

import os
import shutil
from transfer.download import download_file

class Peer_vt(cmd.Cmd):
    intro = "Welcome to the virtual terminal! Type 'help' to see a list of commands."
    prompt = "peer> "
    
    def __init__(self, mode):
        super().__init__()
        assert isinstance(mode, peer.Peer)
        self._peer = mode
     
    def do_help(self, arg):
        args = arg.split()
        if len(args) == 0:
            commands = {
                "connect":"connect to a tracker.",
                "exit":"exit terminal.",
                "list_peers":"display a list of connected peers.",
                "ping":"ping to a specific ip address.",
                "download <filename> <author-ip>":"download a specified file.",
                "upload <filename>":"upload a specified file.",
                "help <command>":"display the command syntax."
            }
            print()
            print("~~ Help menu ~~")
            for cmd, desc in commands.items():
                print(f"  {cmd:10} - {desc}")
            print()
            
        if arg == "connect":
            print()
            print("connect <tracker-ip> <tracker-port>")
            print("<tracker-ip>: The ip address of the tracker.")
            print("<tracker-port>: The port of the tracker.")
            print()
            
        if arg == "exit":
            print()
            print("exit")
            print("This command doesn\'t require any arguments.")
            print()
        
        if arg == "list_peers":
            print()
            print("list_peers")
            print("This command doesn\'t require any arguments.")
            print()
        
        if arg == "ping":
            print()
            print("ping <peer-index>")
            print("<peer-index>: The index of a peer in connected peers list.")
            print()
        
        if arg == "download":
            print()
            print("download <file-name> <author-ip>")
            print("<file-name>: File to download.")
            print("<author-ip>: The ip address of the machine which uploads the file.")
            print()
        
        if arg == "upload":
            print()
            print("upload <file-name>")
            print("<file-name>: File to upload.")
            print()
    
    def do_connect(self, arg):
        #print("connect")
        args = arg.split()
        if len(args) != 2:
            print()
            print("Usage: connect <server ip> <server port>")
            print()
            return

        server_ip = args[0]
        server_port = int(args[1])

        print()
        try:
            print("Connecting to tracker")
            self._peer.connect_server(server_ip, server_port)
            print("Tracker connected")
        except Exception as e:
            print(f"Error connecting to tracker:{e}")
        print()

    def do_exit(self, arg):
        print()
        try:
            print("Exiting...")
            self._peer.exit()
        except Exception as e:
            print(f"Error while exiting: {e}")
        print()
        return True
    
    def do_list_peers(self, arg):
        print()
        try:
            if self._peer.is_connected:
                print("Retreiving connected peers")
                print()
                
                list_peers, list_peers_files = self._peer.get_list_peers()

                if len(list_peers) == 0:
                    print("There are no peer connected to that tracker!!!")
                    print()
                else:
                    print("Peer list:")
                    for i in range(len(list_peers)):
                        print(i+1, list_peers[i][0],":",list_peers[i][1])
                        for p in list_peers_files:
                            if p["author"][0] == list_peers[i][0] and p["author"][1] == list_peers[i][1]:
                                print(f"  - File name: {p['file name']}, file size: {p['file size']}KB")
            else:
                print("This peer is not connected to any tracker")
        except Exception as e:
            print(f"Error retreiving connected peers list: {e}")
        
        print()
    
    def do_ping(self, arg):
        print("ping")
    
    def do_download(self, arg):
        args = arg.split()
        if len(args) != 2:
            print()
            print("Usage: download <filename> <author-ip>")
            print()
            return

        filename, author_ip = args
        destination_folder = "downloaded_files"  # Use only one folder here
        author_port = 22237  # Fixed port for file transfers

        print()
        try:
            file_path = download_file(author_ip, author_port, filename, destination_folder)
            print(f"Downloaded file saved at: {file_path}")
        except Exception as e:
            print(f"Error during file download:{e}")

        print()
    
    def do_upload(self, arg):
        args = arg.split()
        if len(args) != 1:
            print()
            print("Usage: upload <filepath>")
            print()
            return

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

