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
        self.list_peers = []
        self.list_peers_files = []
        self.list_peers_receive = 0
        self._peers_receive = 0
        self._peer_ping_check = 0
        self._tracker_sent = ""
        
    def listen_tracker(self):
        try:
            while self.is_connected:
                pakage = self.client_socket.recv(1024).decode()
                if not pakage:
                    self.is_connected = False
                    break
                message = json.loads(pakage)
                if message["type"] == "LIST_PEERS_RESPONSE":
                    self.list_peers = message["data"][0]
                    self.list_peers_files = message["data"][1]
                    self._peers_receive = 1
                    self.list_peers_receive = 1
                elif message["type"] == "PING":
                    response = {
                        "type":"PONG",
                        "from":self.ip_add,
                        "port":self.port
                    }
                    self.send_to_tracker(response)
                elif message["type"] == "THIS_FILE_HAS_ALREADY_BEEN_UPLOADED":
                    self._peers_receive = 1
                    self._tracker_sent = message["type"]
                elif message["type"] == "TRACKER_HAS_RECEIVED_YOUR_FILE":
                    self._peers_receive = 1
                    self._tracker_sent = message["type"]
                elif message["type"] == "TRACKER_EXIT":
                    self.client_socket.close()
                    self.is_connected = False
                    break
        except OSError as e:
            if e.winerror != 10053:
                print(f"Error receiving data from tracker [OSError]: {e}")
            pass
        except Exception as e:
            print(f"Error receiving data from tracker: {e}")
    
    def connect_server(self, host, port):
        self.client_socket.connect((host, port))
        self.ip_add, self.port = self.client_socket.getsockname()
        self.is_connected = True
        listen = Thread(target=self.listen_tracker, daemon=True)
        listen.start()
            
    def send_to_tracker(self, message):
        pakage = json.dumps(message)
        self.client_socket.sendall(pakage.encode())

    def get_list_peers(self):
        message = {
            "type": "LIST_PEERS",
            "from": self.ip_add,
            "port": self.port
        }
        self.send_to_tracker(message)
        while self.list_peers_receive == 0:
            pass
        self.list_peers_receive = 0
        return (self.list_peers, self.list_peers_files)

    def exit(self):
        if self.is_connected:
            message = {
                "type": "PEER_EXIT",
                "from": self.ip_add,
                "port": self.port
            }
            self.send_to_tracker(message)
            # self.upload_server.stop()
            self.is_connected = False
            self.client_socket.close()