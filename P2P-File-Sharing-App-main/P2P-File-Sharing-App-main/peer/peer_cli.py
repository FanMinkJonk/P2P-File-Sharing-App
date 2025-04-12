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
                "connect":"connect to a server",
                "exit":"exit terminal",
                "list_peers":"display a list of connected peers",
                "ping":"ping to a specific ip address",
                "download <filename> <author-ip>":"download a specified file",
                "upload <filename>":"upload a specified file",
                "help <command>":"display the command syntax"
            }
            print("\nList of command :")
            for cmd, desc in commands.items():
                print(f"  {cmd:10} - {desc}")
            print()
            
        if arg == "connect":
            print("connect --server-ip <ip> --server-port <port>")
            print()
            
        if arg == "exit":
            print("exit")
            print()
        
        if arg == "list_peers":
            print("list_peers")
            print()
        
        if arg == "ping":
            print("ping --client-ip --client-port")
            print()
        
        if arg == "download":
            print("download --destination-folder --filename --author-ip")
            print()
        
        if arg == "upload":
            print("upload --filename")
            print()
    
    def do_connect(self, arg):
        #print("connect")
        args = arg.split()
        if len(args) != 2:
            print("Usage: connect <server ip> <server port>")
            return

        server_ip = args[0]
        server_port = int(args[1])

        try:
            print("Connecting to tracker")
            self._peer.connect_server(server_ip, server_port)
        except Exception as e:
            print("Error connecting to tracker: ",e)

    def do_exit(self, arg):
        try:
            print("Exiting...")
            self._peer.exit()
            print()
            return True
        except Exception as e:
            print(f"Error while exiting: {e}")
    
    def do_list_peers(self, arg):
        try:
            if self._peer.is_connected:
                print("Retreiving connected peers")
                print()
                list_peers = self._peer.get_list_peers()
                if len(list_peers) == 0:
                    print("There are no peer connected to this tracker!!!")
                else:
                    print("Peer list:")
                    for i in range(len(list_peers)):
                        print(i+1, list_peers[i][0],":",list_peers[i][1])
                    print()
            else:
                print("This peer is not connected to any tracker")
        except Exception as e:
            print("Error retreiving connected peers list: ", e)
    
    def do_ping(self, arg):
        print("ping")
    
    def do_download(self, arg):
        print("download")
    
    def do_upload(self, arg):
        print("upload")

# if __name__ == "__main__":
#     Peer_vt.cmdloop()

##########################################################################################

def new_do_download(self, arg):
    args = arg.split()
    if len(args) != 2:
        print("Usage: download <filename> <author-ip>")
        return

    filename, author_ip = args
    destination_folder = "downloaded_files"  # Use only one folder here
    author_port = 22237  # Fixed port for file transfers

    try:
        from transfer.download import download_file
        file_path = download_file(author_ip, author_port, filename, destination_folder)
        print(f"Downloaded file saved at: {file_path}")
    except Exception as e:
        print("Error during file download:", e)

def new_do_upload(self, arg):
    args = arg.split()
    if len(args) != 1:
        print("Usage: upload <filepath>")
        return

    # Get the file path from input argument
    filepath = args[0]
    destination_folder = "shared_files"  # Folder where the upload server serves files

    try:
        # Ensure the destination folder exists; if not, create it
        if not os.path.exists(destination_folder):
            os.makedirs(destination_folder)
        # Copy the file into the shared folder
        shutil.copy(filepath, destination_folder)
        print(f"File '{filepath}' uploaded successfully to '{destination_folder}'.")
    except Exception as e:
        print("Error during file upload:", e)

# Monkey-patch the Peer CLI class (assumed to be Peer_vt) with the new file transfer commands.
Peer_vt.do_download = new_do_download
Peer_vt.do_upload = new_do_upload