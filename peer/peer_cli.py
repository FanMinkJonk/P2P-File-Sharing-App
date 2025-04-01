import cmd

class Peer_vt(cmd.Cmd):
    intro = "Welcome to the virtual terminal! Type 'help' to see a list of commands."
    prompt = "peer> "
    
    def __init__(self):
        super().__init__()
     
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
        print("connect")

    def do_exit(self, arg):
        print("exit")
        return True
    
    def do_list_peers(self, arg):
        print("list peers")
    
    def do_ping(self, arg):
        print("ping")
    
    def do_download(self, arg):
        print("download")
    
    def do_upload(self, arg):
        print("upload")

# if __name__ == "__main__":
#     Peer_vt.cmdloop()
