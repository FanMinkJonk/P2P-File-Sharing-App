# upload.py
import socket
import json
import os
from threading import Thread

class UploadServer:
    def __init__(self, host="", port=22237, files_folder="shared_files"):
        self.host = host if host else self.get_default_ip()
        self.port = port
        self.files_folder = files_folder
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Allow reuse of the socket address
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.server_running = False

    def get_default_ip(self):
        #Detects the default IP address of this machine.
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(('8.8.8.8', 80))
            ip = s.getsockname()[0]
        except Exception:
            ip = '127.0.0.1'
        finally:
            s.close()
        return ip

    def start(self):
        #Starts the upload server to listen for incoming file download requests.
        # Ensure the shared files folder exists
        if not os.path.exists(self.files_folder):
            os.makedirs(self.files_folder)
        try:
            self.server_socket.bind((self.host, self.port))
            self.server_socket.listen(5)
            self.server_running = True
            print(f"Upload server listening on {self.host}:{self.port}")
            while self.server_running:
                try:
                    client_socket, client_addr = self.server_socket.accept()
                    print(f"Received connection from {client_addr}")
                    # Handle each client connection in a separate thread
                    thread = Thread(target=self.handle_client, args=(client_socket,), daemon=True)
                    thread.start()
                except Exception as e:
                    print(f"Error accepting connection: {e}")
        except Exception as e:
            print("Error starting upload server:", e)
            self.server_socket.close()

    def handle_client(self, client_socket):
        #Handles an individual client's download request.
        try:
            data = client_socket.recv(1024).decode()
            if data:
                try:
                    request = json.loads(data)
                except json.JSONDecodeError:
                    print("Invalid JSON received from client.")
                    client_socket.close()
                    return

                # Process a download request
                if request.get("type") == "DOWNLOAD_REQUEST":
                    filename = request.get("filename")
                    file_path = os.path.join(self.files_folder, filename)
                    if os.path.exists(file_path) and os.path.isfile(file_path):
                        filesize = os.path.getsize(file_path)
                        response = {
                            "type": "DOWNLOAD_RESPONSE",
                            "status": "OK",
                            "filesize": filesize
                        }
                        client_socket.sendall(json.dumps(response).encode())
                        # Now, send the file data in chunks
                        with open(file_path, "rb") as f:
                            while True:
                                chunk = f.read(4096)
                                if not chunk:
                                    break
                                client_socket.sendall(chunk)
                        print(f"File '{filename}' sent successfully.")
                    else:
                        # File not found, send error response
                        response = {
                            "type": "DOWNLOAD_RESPONSE",
                            "status": "ERROR",
                            "error": "File not found."
                        }
                        client_socket.sendall(json.dumps(response).encode())
                else:
                    print("Unknown request type received.")
            client_socket.close()
        except Exception as e:
            print(f"Error handling client: {e}")
            client_socket.close()

    def stop(self):
        #Stops the upload server.
        self.server_running = False
        self.server_socket.close()
        print("Upload server stopped.")

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Upload Server for handling file transfers (serving shared files).")
    parser.add_argument("--host", type=str, default="", help="Host IP to listen on. If not provided, it will be auto-detected.")
    parser.add_argument("--port", type=int, default=22237, help="Port number to listen on for file uploads.")
    parser.add_argument("--files_folder", type=str, default="shared_files", help="Folder where shared files are stored.")
    args = parser.parse_args()

    server = UploadServer(host=args.host, port=args.port, files_folder=args.files_folder)
    try:
        server.start()
    except KeyboardInterrupt:
        server.stop()