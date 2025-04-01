import socket
import argparse

from threading import Thread

class Peer:
    def __init__(self):
        self.client_socket = socket.socket()
        
    def connect_server(self, host, port):
        try:
            self.client_socket.connect((host, port))
            print("Tracker connected")
        except Exception as e:
            print("Error, can't connect to tracker: ",e)