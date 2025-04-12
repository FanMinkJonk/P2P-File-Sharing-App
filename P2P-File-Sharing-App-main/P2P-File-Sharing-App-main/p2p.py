import argparse
import sys

# Peer
import peer.peer_cli as peer_vt
import peer.peer_be as peer

# Tracker
import tracker.tracker_cli as tracker_vt
import tracker.tracker_be as tracker

def run():
    global loop, mode
    
    arg_parser = argparse.ArgumentParser(description="tracker or peer")
    arg_parser.add_argument('mode')
    
    num_args = len(sys.argv) - 1
    arg = arg_parser.parse_args()
    
    if num_args != 1:
        print()
        print("Invalid input")
        print("Option must be either \'tracker\' or \'peer\' !!")
        print()
    if arg.mode == "tracker":
        #TODO
        print()
        print("Tracker mode")
        mode = tracker.Tracker()
        mode_t = tracker_vt.Tracker_t(mode)
        
    elif arg.mode == "peer":
        #TODO
        print()
        print("Peer mode")
        mode = peer.Peer()
        mode_t = peer_vt.Peer_vt(mode)
        
    try:
        mode_t.cmdloop()
    except (KeyboardInterrupt, EOFError):
        pass
    except Exception as e:
        print('{}:{}'.format(type(e).__name__, e))
    
        
if __name__ == "__main__":
    run()