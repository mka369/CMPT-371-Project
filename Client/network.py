## Handle network requests
import socket
import threading
import json
from shared.protocol import encode_message, decode_message
from shared.constants import SERVER_PORT, SERVER_ADDRESS

class NetworkClient():
    def __init__(self, host=SERVER_ADDRESS, port=SERVER_PORT):
        ## Initialize the network client with the server address.
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((host, port))
        self.listener = threading.Thread(target=self.listen)
        self.listener.start()
        self.game_state = {}
        self.running = True

    def send(self, data: dict):
        ## Send data to the server.
        self.sock.sendall(encode_message(data))

    def listen(self):
        ## Listen for incoming data from the server.
        while self.running:
            try:
                msg = self.sock.recv(4096)
                if not msg:
                    self.running = False
                    break
                if msg:
                    self.game_state = decode_message(msg)
            except:
                break

    def get_game_state(self):
        ## Get the current game state from the server.
        return self.game_state
    
    def close(self):
        ## Shuts down connection
        self.running = False
        self.sock.shutdown(socket.SHUT_RDWR)
        self.sock.close()
        self.listener.join()