import argparse
import sys

# Peer


# Tracker


def run():
    global loop, mode
    
    arg_parser = argparse.ArgumentParser(description="tracker or peer")
    arg_parser.add_argument('mode')
    
    num_args = len(sys.argv) - 1
    arg = arg_parser.parse_args()
    
    if num_args != 1:
        print("Invalid input")
        print("Option must be either \'tracker\' or \'peer\' !!")
    if arg.mode == "tracker":
        #TODO
        print("Tracker mode")
        
    elif arg.mode == "peer":
        #TODO
        print("Peer mode")
        
    
        
if __name__ == "__main__":
    run()