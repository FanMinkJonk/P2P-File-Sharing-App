# download.py
import socket
import json
import os

def download_file(author_ip, author_port, filename, destination_folder):   
    # Create the destination folder if it does not exist
    if not os.path.exists(destination_folder):
        os.makedirs(destination_folder)
    
    # Create a socket to connect to the file-hosting peer
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        try:
            s.connect((author_ip, author_port))
        except Exception as e:
            raise Exception(f"Error connecting to peer at {author_ip}:{author_port} - {e}")
        
        # Send a download request as a JSON message
        request = {
            "type": "DOWNLOAD_REQUEST",
            "filename": filename
        }
        request_json = json.dumps(request)
        s.sendall(request_json.encode())
        
        # Receive a response from the file server (peer)
        response_data = s.recv(1024).decode()
        try:
            response = json.loads(response_data)
        except json.JSONDecodeError:
            raise Exception("Invalid response received from the file server.")
        
        if response.get("type") != "DOWNLOAD_RESPONSE":
            raise Exception("Unexpected response type from the file server.")
        
        if response.get("status") != "OK":
            error_msg = response.get("error", "Unknown error")
            raise Exception(f"File download request failed: {error_msg}")
        
        # Get the file size from the response
        filesize = int(response.get("filesize", 0))
        if filesize <= 0:
            raise Exception("Invalid file size received.")
        
        # Open the file to write the received data
        file_path = os.path.join(destination_folder, filename)
        bytes_received = 0
        with open(file_path, "wb") as f:
            while bytes_received < filesize:
                # Read data in chunks (up to 4096 bytes at a time)
                chunk = s.recv(min(4096, filesize - bytes_received))
                if not chunk:
                    break
                f.write(chunk)
                bytes_received += len(chunk)
        
        if bytes_received != filesize:
            raise Exception("File download was incomplete or interrupted.")
        
        return file_path

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Download file from a peer.")
    parser.add_argument("--author-ip", type=str, required=True, help="IP address of the peer hosting the file.")
    parser.add_argument("--author-port", type=int, required=True, help="Port of the file-hosting peer.")
    parser.add_argument("--filename", type=str, required=True, help="Name of the file to download.")
    parser.add_argument("--destination-folder", type=str, default="downloads", help="Folder to save the downloaded file.")
    
    args = parser.parse_args()
    try:
        file_path = download_file(args.author_ip, args.author_port, args.filename, args.destination_folder)
        print(f"File downloaded successfully: {file_path}")
    except Exception as e:
        print(f"Error while downloading file: {e}")


#---------------------------------------------------------
# Torrent download
def download_piece(ip, port, filename, piece_index, default_piece_size=512*1024):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        sock.connect((ip, port))
    except Exception as e:
        sock.close()
        raise Exception(f"Error connecting to peer at {ip}:{port} - {e}")
    
    # Send a piece request as a JSON message (terminated by newline)
    request = {
        "type": "PIECE_REQUEST",
        "filename": filename,
        "piece_index": piece_index
    }
    sock.sendall((json.dumps(request) + "\n").encode("utf-8"))
    
    # Receive JSON response (terminated by newline)
    response_data = ""
    while "\n" not in response_data:
        chunk = sock.recv(1024).decode("utf-8")
        if not chunk:
            break
        response_data += chunk
    try:
        response = json.loads(response_data.strip())
    except json.JSONDecodeError:
        sock.close()
        raise Exception("Invalid response received from the peer for piece download.")
    
    if response.get("status") != "OK":
        sock.close()
        raise Exception(response.get("error", "Error downloading piece"))
    
    piece_size = response.get("piece_size", default_piece_size)
    data = b""
    remaining = piece_size
    while remaining > 0:
        chunk = sock.recv(min(4096, remaining))
        if not chunk:
            break
        data += chunk
        remaining -= len(chunk)
    
    sock.close()
    return data