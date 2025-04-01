import peer.peer_be as peer
import cmd

class Peer_vt(cmd.Cmd):
    intro = "Welcome to the virtual terminal! Type 'help' to see a list of commands."
    prompt = "peer> "
    
    def __init__(self, mode):
        super().__init__()
        self._peer = mode
     
    def do_help(self, arg):
        args = arg.split()
        if len(args) == 0:
            commands = {
                "connect":"connect to a server",
                "exit":"exit terminal",
                "list_peers":"display a list of connected peers",
                "ping":"ping to a specific ip address",
                "download":"download a specified file",
                "upload":"upload a specified file",
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
        print("exit")
        return True
    
    def do_list_peers(self, arg):
        try:
            print("Retreiving connected peers")
            list_peers = self._peer.send_to_tracker("LIST_PEERS")
            if len(list_peers) == 0:
                print("There are no peer connected to this tracker!!!")
            else:
                print("")
                print("Peer list:")
                for i in range(len(list_peers)):
                    print(list_peers[i][0],":",list_peers[i][1])
                print("")
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
