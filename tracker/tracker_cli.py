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
                "start":"start listening for income",
                "exit":"exit terminal",
                "list_peers":"display a list of connected peers",
                "ping":"ping to a specific ip address",
                "help <command>":"display the command syntax"
            }
            print("\nList of command :")
            for cmd, desc in commands.items():
                print(f"  {cmd:10} - {desc}")
            print()
            
        if arg == "start":
            print("start")
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

    def do_start(self, arg):
        #print("start")
        args = arg.split()
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

    def do_exit(self, arg):
        print("Exiting...")
        #TODO
        args = arg.split()
        if len(args) == 0:
            try:
                self._tracker.stop_server()
            except Exception as e:
                print("Error: {e}")
        else:
            print("This command doesn't require any arguments !!!")
            return
        return True

    def do_list_peers(self, arg):
        print("list peers")
        #TODO
        args = arg.split()
        if len(args) == 0:
            try:
                _peer_list = self._tracker.get_list_peers()
                if not self._tracker.is_running:
                    print("Tracker is currently offline!!!")
                else:
                    if len(_peer_list) == 0:
                        print("There are no peer connected to this tracker!!!")
                    else:
                        for p in _peer_list:
                            print(p)
            except Exception as e:
                print("Error while listing peers: {e}")
        else:
            print("This command doesn't require any arguments !!!")
            return

    def do_ping(self, arg):
        print("ping")
        #TODO
