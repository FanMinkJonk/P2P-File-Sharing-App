import socket
import json
from threading import Thread

# Errors Handling
class ServerIsRunning(Exception):
    def __init__(self, message="Server is already running"):
        super().__init__(message)

class Tracker:
    def __init__(self):
        # Tracker's ip:port
        self._host = ""
        self._port = -1

        # Check if tracker is running
        self.is_running = False
        
        # Stores a list of peers and there uploaded files
        self._peer_addrs = []
        self._peer_sockets = []
        self._peer_files = []
        
        # Ping to peer
        self.ping_check = 0

    # Send message
    def send_to_peer(self, conn, message):
        package = json.dumps(message)
        conn.sendall(package.encode())

    # New connection in a separate thread
    def listen_peer(self, addr, conn):
        self._peer_addrs.append(addr)
        self._peer_sockets.append(conn)
        while True:
            try:
                pakage = conn.recv(1024).decode()
                if pakage:
                    message = json.loads(pakage)
                    if message["type"] == "LIST_PEERS":
                        response = {
                            "type":"LIST_PEERS_RESPONSE",
                            "from":self._host,
                            "port":self._port,
                            "data":[self._peer_addrs, self._peer_files]
                        }
                        self.send_to_peer(conn, response)
                    elif message["type"] == "PONG":
                        self.ping_check = 1
                    elif message["type"] == "PEER_EXIT":
                        self._peer_addrs.remove(addr)
                        self._peer_sockets.remove(conn)
                        break
                    elif message["type"] == "PEER_UPLOAD":
                        metainfo = {
                            "author":[message["from"], message["port"]],
                            "file name":message["data"][0],
                            "file size":message["data"][1],
                        }
                        if metainfo in self._peer_files:
                            response = {
                                "type":"THIS_FILE_HAS_ALREADY_BEEN_UPLOADED",
                                "from":self._host,
                                "port":self._port,
                            }
                            self.send_to_peer(conn, response)
                        else:
                            self._peer_files.append(metainfo)
                            response = {
                                "type":"TRACKER_HAS_RECEIVED_YOUR_FILE",
                                "from":self._host,
                                "port":self._port,
                            }
                            self.send_to_peer(conn, response)
                                            
            except socket.error:
                pass
            except Exception as e:
                print(f'Error occured while listening to peer {addr} :',e)
                break

    # Listens for in coming connection
    def listen_for_con(self):
        self.serversocket=socket.socket()
        self.serversocket.settimeout(1.0)
        self.serversocket.bind((self._host, self._port))
        self.serversocket.listen(10)
        
        while self.is_running:
            try:
                clientsocket, addr = self.serversocket.accept()
                nconn = Thread(target = self.listen_peer, args = (addr, clientsocket), daemon=True)
                nconn.start()
            except OSError:
                continue

    # Start server
    def start_server(self):
        if self.is_running == False:
            self.is_running = True
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            try:
                s.connect(('8.8.8.8', 1))
                ip = s.getsockname()[0]
            except Exception:
                raise Exception
            finally:
                s.close()
            self._host = ip
            self._port = 22236
            print("Listening on: {}:{}".format(self._host, self._port))
            self.server_thread = Thread(target = self.listen_for_con, daemon=True)
            self.server_thread.start()
        else:
            raise ServerIsRunning

    # Stop server
    def stop_server(self):
        if self.is_running == True:
            self.is_running = False
            message = {
                "type":"TRACKER_EXIT",
                "from":self._host,
                "port":self._port
            }
            for i in range(len(self._peer_sockets)):
                self.send_to_peer(self._peer_sockets[i], message)
            self.serversocket.close()
            self.server_thread.join()
    
    # Ping to peer
    def ping(self, peer_index):
        message = {
            "type":"PING",
            "from":self._host,
            "port":self._port
        }
        self.send_to_peer(self._peer_sockets[peer_index], message)
        while self.ping_check == 0:
            pass
        return self.ping_check