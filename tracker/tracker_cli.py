import tracker.tracker_be as tracker
import cmd

class Tracker_t(cmd.Cmd):
    intro = "Welcome to the virtual terminal! Type 'help' to see a list of commands."
    prompt = "tracker> "

    def __init__(self, mode):
        super().__init__()
        assert isinstance(mode, tracker.Tracker)
        self._tracker = mode

    def do_help(self, arg):
        args = arg.split()
        if len(args) == 0:
            commands = {
                "start":"start listening for incoming connection.",
                "exit":"exit terminal.",
                "list_peers":"display a list of connected peers.",
                "ping <peer_index>":"ping to a specific ip address.",
                "help <command>":"display the command syntax."
            }
            print()
            print("~~ Help menu ~~")
            for cmd, desc in commands.items():
                print(f"  {cmd:10} - {desc}")
            print()
            
        if arg == "start":
            print()
            print("start")
            print("This command doesn\'t require any argument")
            print()
            
        if arg == "exit":
            print()
            print("exit")
            print("This command doesn\'t require any argument.")
            print()
        
        if arg == "list_peers":
            print()
            print("list_peers")
            print("This command doesn\'t require any argument.")
            print()
        
        if arg == "ping":
            print()
            print("ping <peer_index>")
            print("<peer-index>: The index of a peer in connected peers list.")
            print()

    def do_start(self, arg):
        args = arg.split()
        
        print()
        if len(args) == 0:
            try:
                self._tracker.start_server()
            except tracker.ServerIsRunning:
                print("Tracker is already up and running!!")
            except Exception as e:
                print("Error: {e}")
        else:
            print("This command doesn't require any arguments !!!")
            return
        print()

    def do_exit(self, arg):
        print()
        print("Exiting...")
        
        args = arg.split()
        if len(args) == 0:
            try:
                self._tracker.stop_server()
            except Exception as e:
                print("Error when exiting:",e)
        else:
            print("This command doesn't require any arguments !!!")
            return
        print()
        
        return True

    def do_list_peers(self, arg):
        args = arg.split()
        
        print()
        if len(args) == 0:
            try:
                _peer_list = self._tracker.get_list_peers()
                if not self._tracker.is_running:
                    print("Tracker is currently offline!!!")
                else:
                    if len(_peer_list) == 0:
                        print("There are no peer connected to this tracker!!!")
                    else:
                        print("Peer list:")
                        for i in range(len(_peer_list)):
                            print(i+1, _peer_list[i][0],":",_peer_list[i][1])
                            for p in self._tracker._peer_files:
                                if p["author"][0] == _peer_list[i][0] and p["author"][1] == _peer_list[i][1]:
                                    print(f"  - File name: {p['file name']}, file size: {p['file size']}KB")
            except Exception as e:
                print(f"Error while listing peers: {e}")
        else:
            print("This command doesn't require any arguments !!!")
            return
        print()

    def do_ping(self, arg):
        args = arg.split()
        
        print()
        if len(args) == 1:
            try:
                _peer_list = self._tracker.get_list_peers()
                if not self._tracker.is_running:
                    print("Tracker is currently offline!!!")
                elif len(_peer_list) == 0:
                    print("There are no peer connected to this tracker!!!")
                else:
                    check = self._tracker.ping(int(args[0])-1)
                    if check:
                        print(f"Succesfully ping to {self._tracker._peer_addrs[int(args[0])-1][0]}:{self._tracker._peer_addrs[int(args[0])-1][1]}")
                    self._tracker.ping_check = 0
            except Exception as e:
                print(f"Error while ping to peer: {e}")
        else:
            print("Usage: ping <peer_index>")
        print()
