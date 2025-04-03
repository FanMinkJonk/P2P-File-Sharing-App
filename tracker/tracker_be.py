import socket
import json
from threading import Thread

# Errors Handling
class ServerIsRunning(ConnectionError):
    pass

class Tracker:
    def __init__(self):
        self._host = ""
        self._port = -1

        self.server = None
        self.writer = set()

        # Check if server is running
        self.is_running = False
        
        # Stores a list of peers and there uploaded files
        self._peer_list = []

    # New connection in a separate thread
    def new_connection(self, addr, conn):
        self._peer_list.append(addr)
        
        while True:
            try:
                pakage = conn.recv(1024).decode()
                message = json.loads(pakage)
                if message["type"] == "LIST_PEERS":
                    response = {
                        "type":"LIST_PEERS_RESPONSE",
                        "from":self._host,
                        "port":self._port,
                        "data":self._peer_list
                    }
                    pakage = json.dumps(response)
                    conn.sendall(pakage.encode())
                
                # Todo: process at tracker side
            except Exception as e:
                print('Error occured: ',e)
                break

    # Listens for on coming connectiong
    def listen_for_con(self):
        self.serversocket=socket.socket()
        self.serversocket.settimeout(1.0)
        self.serversocket.bind((self._host, self._port))
        self.serversocket.listen(10)
        
        while self.is_running:
            try:
                clientsocket, addr = self.serversocket.accept()
                nconn = Thread(target = self.new_connection, args = (addr, clientsocket), daemon=True)
                nconn.start()
            except OSError:
                continue

    # Get host ip
    def get_host_default_interface_ip(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(('8.8.8.8', 1))
            ip = s.getsockname()[0]
        except Exception:
            ip = '127.0.0.1'
        finally:
            s.close()
        return ip

    # Start server
    def start_server(self):
        if self.is_running == False:
            self.is_running = True
            self._host = self.get_host_default_interface_ip()
            self._port = 22236
            print("Listening on: {}:{}".format(self._host, self._port))
            self.server_thread = Thread(target = self.listen_for_con, daemon=True)
            self.server_thread.start()
        else:
            raise ServerIsRunning

    def stop_server(self):
        if self.is_running == True:
            self.is_running = False
            self.serversocket.close()
            self.server_thread.join()
    
    def get_list_peers(self):
        return self._peer_list
