import socket
import argparse
import json
import os
import shutil


from transfer.download import download_file
from threading import Thread

from transfer.upload import UploadServer
import threading

class Peer:
    def __init__(self):
        self.client_socket = socket.socket()
        self.is_connected = False
        self.ip_add = ""
        self.port = -1
        
        # Shared memory for tracker responses
        self.list_peers = []
        self.list_peers_files = []
        self.list_peers_receive = 0

    def listen_tracker(self):
        while self.is_connected:
            pakage = self.client_socket.recv(1024).decode()
            message = json.loads(pakage)
            if message["type"] == "LIST_PEERS_RESPONSE":
                self.list_peers = message["data"][0]
                self.list_peers_files = message["data"][1]
                self.list_peers_receive = 1
            elif message["type"] == "PING":
                response = {
                    "type": "PONG",
                    "from": self.ip_add,
                    "port": self.port
                }
                self.send_to_tracker(response)
            elif message["type"] == "TRACKER_EXIT":
                self.client_socket.close()
                self.is_connected = False
                break

    def connect_server(self, host, port):
        self.client_socket.connect((host, port))
        self.ip_add, self.port = self.client_socket.getsockname()
        self.is_connected = True
        listen = Thread(target=self.listen_tracker, daemon=True)
        listen.start()
        print()
        print("Tracker connected")
        print()

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

    def upload(self, filepath, destination_folder):
        file_name = os.path.basename(filepath)
        file_size = os.path.getsize(filepath)
        message = {
            "type": "PEER_UPLOAD",
            "from": self.ip_add,
            "port": self.port,
            "data": [file_name, file_size]
        }
        self.send_to_tracker(message)
        if not os.path.exists(destination_folder):
            os.makedirs(destination_folder)
        shutil.copy(filepath, destination_folder)
        return 1

    def exit(self):
        if self.is_connected:
            message = {
                "type": "PEER_EXIT",
                "from": self.ip_add,
                "port": self.port
            }
            self.send_to_tracker(message)
            self.client_socket.close()
            self.is_connected = False

    # Updated ping method without using send_message.
    def ping(self, peer_index):
        try:
            target_peer = tuple(self.list_peers[peer_index - 1])  # 1-indexed
        except IndexError:
            return "Peer not found."
        try:
            message = {"type": "PING"}
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect(target_peer)  # target_peer is a tuple (ip, port)
            s.sendall((json.dumps(message) + "\n").encode("utf-8"))
            response_data = ""
            while "\n" not in response_data:
                response_data += s.recv(1024).decode("utf-8")
            s.close()
            response = json.loads(response_data.strip())
            return response.get("status", "No reply")
        except Exception as e:
            return f"Error: {e}"


def start_upload_for_peer(peer_instance):
    peer_instance.upload_server = UploadServer(port=22237, files_folder="shared_files")
    threading.Thread(target=peer_instance.upload_server.start, daemon=True).start()


# Override Peer.__init__ to start the upload server automatically.
if hasattr(Peer, '__init__'):
    original_init = Peer.__init__
    def new_init(self, *args, **kwargs):
        original_init(self, *args, **kwargs)
        start_upload_for_peer(self)
    Peer.__init__ = new_init