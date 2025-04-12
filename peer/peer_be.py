import os
from utils import split_file_to_pieces, save_metadata
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

 # Upload file chia theo mảnh torrent
    def upload_file(self, filename):
        try:
            shared_path = os.path.join("shared", filename)
            if not os.path.exists(shared_path):
                print(f"[ERROR] File not found: {shared_path}")
                return

            pieces_info, filesize = split_file_to_pieces(shared_path)
            meta_path = save_metadata(filename, filesize, pieces_info, self.ip_add, self.port)
            print(f"[UPLOAD COMPLETE] Metadata saved at: {meta_path}")
        except Exception as e:
            print(f"[ERROR] Upload failed: {e}")

# Download file từ metadata torrent
    def download_file(self, torrent_filename):
        try:
            torrent_path = os.path.join("metadata", torrent_filename)
            with open(torrent_path, 'r') as f:
                metadata = json.load(f)

            file_name = metadata["filename"]
            total_pieces = len(metadata["pieces"])
            output_path = os.path.join("downloads", file_name)
            os.makedirs("downloads", exist_ok=True)

            with open(output_path, 'wb') as out_file:
                for piece in metadata["pieces"]:
                    index = piece["index"]
                    owner = piece["owner"]
                    host, port = owner.split(":")
                    port = int(port)

                    try:
                        with socket.create_connection((host, port), timeout=5) as s:
                            request = f"Request {index}"
                            s.sendall(request.encode())
                            header = s.recv(64).strip()
                            if b"header:OK" in header:
                                piece_data = b""
                                while True:
                                    chunk = s.recv(4096)
                                    if not chunk:
                                        break
                                    piece_data += chunk

                                out_file.seek(index * 512 * 1024)
                                out_file.write(piece_data)
                                print(f"[DOWNLOADED] Piece {index} from {host}:{port}")
                            else:
                                print(f"[FAILED] Piece {index} not found on {host}:{port}")
                    except Exception as e:
                        print(f"[ERROR] Could not download piece {index} from {host}:{port}: {e}")

            print(f"[DOWNLOAD COMPLETE] File saved to downloads/{file_name}")
        except Exception as e:
            print(f"[ERROR] Download failed: {e}")