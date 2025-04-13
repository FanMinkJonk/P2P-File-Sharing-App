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
        self.upload_server = UploadServer(port=22237, files_folder="shared_files")
        threading.Thread(target=self.upload_server.start, daemon=True).start()
        
        # Shared memory
        self.list_peers = []
        self.list_peers_files = []
        self._peers_receive = 0
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
            "type":"LIST_PEERS",
            "from":self.ip_add,
            "port":self.port
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
            "type":"PEER_UPLOAD",
            "from":self.ip_add,
            "port":self.port,
            "data":[file_name, file_size]
        }
        self.send_to_tracker(message)
        
        while self._peers_receive == 0:
            pass
        
        self._peers_receive = 0
        if self._tracker_sent == "TRACKER_HAS_RECEIVED_YOUR_FILE":
            # Ensure the destination folder exists; if not, create it
            if not os.path.exists(destination_folder):
                os.makedirs(destination_folder)
            
            # Copy the file into the shared folder
            shutil.copy(filepath, destination_folder)
            return 1
        elif self._tracker_sent == "THIS_FILE_HAS_ALREADY_BEEN_UPLOADED":
            return 0

    def exit(self):
        if self.is_connected:
            message = {
                "type":"PEER_EXIT",
                "from":self.ip_add,
                "port":self.port
            }
            self.send_to_tracker(message)
            self.upload_server.stop()
            self.is_connected = False
            self.client_socket.close()

############################################################################################
# def start_upload_for_peer(peer_instance):
#     peer_instance.upload_server = UploadServer(port=22237, files_folder="shared_files")
#     # Start the upload server in a separate daemon thread
#     threading.Thread(target=peer_instance.upload_server.start, daemon=True).start()

# # Save the original __init__ if it exists.
# if hasattr(Peer, '__init__'):
#     original_init = Peer.__init__
#     def new_init(self, *args, **kwargs):
#         original_init(self, *args, **kwargs)
#         start_upload_for_peer(self)
#     Peer.__init__ = new_init
