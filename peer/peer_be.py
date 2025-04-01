import socket
import argparse

from threading import Thread

# Errors Handling
class CantGetList(Exception):
    pass

class Peer:
    def __init__(self):
        self.client_socket = socket.socket()
        
    def connect_server(self, host, port):
        try:
            self.client_socket.connect((host, port))
            print("Tracker connected")
        except Exception as e:
            print("Error, can't connect to tracker: ",e)
            
    def send_to_tracker(self, message):
        self.client_socket.sendall(message.encode())
        print(self.client_socket.recv(1024).decode())
            