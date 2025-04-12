import socket
import argparse
import json

from threading import Thread

from transfer.upload import UploadServer
import threading

# Errors Handling
class CantGetList(Exception):
    pass

class Peer:
    def __init__(self):
        self.client_socket = socket.socket()
        self.is_connected = False
        self.ip_add = ""
        self.port = -1
        
        # Shared memory
        self.list_peers = None
        
    def listen_tracker(self):
        while self.is_connected:
            pakage = self.client_socket.recv(1024).decode()
            message = json.loads(pakage)
            if message["type"] == "LIST_PEERS_RESPONSE":
                self.list_peers = message["data"]
            elif message["type"] == "PING":
                response = {
                    "type":"PONG",
                    "from":self.ip_add,
                    "port":self.port
                }
                self.send_to_tracker(response)
            elif message["type"] == "TRACKER_EXIT":
                self.client_socket.close()
                self.is_connected = False
                break
    
    def connect_server(self, host, port):
        try:
            self.client_socket.connect((host, port))
            self.ip_add, self.port = self.client_socket.getsockname()
            self.is_connected = True
            listen = Thread(target=self.listen_tracker, daemon=True)
            listen.start()
            print("Tracker connected")
        except Exception as e:
            print("Error, can't connect to tracker:",e)
            
    def send_to_tracker(self, message):
        pakage = json.dumps(message)
        self.client_socket.sendall(pakage.encode())

    def get_list_peers(self):
        message = {
            "type":"LIST_PEERS",
            "from":self.ip_add,
            "port":self.port
        }
        self.send_to_tracker(message)
        
        while self.list_peers==None:
            pass
        return self.list_peers

    def exit(self):
        if self.is_connected:
            message = {
                "type":"PEER_EXIT",
                "from":self.ip_add,
                "port":self.port
            }
            self.send_to_tracker(message)
            self.client_socket.close()
            self.is_connected = False

############################################################################################
def start_upload_for_peer(peer_instance):
    peer_instance.upload_server = UploadServer(port=22237, files_folder="shared_files")
    # Start the upload server in a separate daemon thread
    threading.Thread(target=peer_instance.upload_server.start, daemon=True).start()

# Save the original __init__ if it exists.
if hasattr(Peer, '__init__'):
    original_init = Peer.__init__
    def new_init(self, *args, **kwargs):
        original_init(self, *args, **kwargs)
        start_upload_for_peer(self)
    Peer.__init__ = new_init
