import socket
import argparse
import json

from threading import Thread

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
    
    def connect_server(self, host, port):
        try:
            self.client_socket.connect((host, port))
            self.ip_add, self.port = self.client_socket.getsockname()
            self.is_connected = True
            listen = Thread(target=self.listen_tracker, daemon=True)
            listen.start()
            print("Tracker connected")
        except Exception as e:
            print("Error, can't connect to tracker: ",e)
            
    def send_to_tracker(self, message):
        pakage = json.dumps(message)
        self.client_socket.sendall(pakage.encode())

    def get_list_peers(self):
        message = {
            "type":"LIST_PEERS",
            "from":self.ip_add,
            "port":str(self.port)
        }
        self.send_to_tracker(message)
        
        while self.list_peers==None:
            pass
        return self.list_peers