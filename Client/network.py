## Handle network requests
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import socket
import threading
from shared.protocol import encode_message, decode_message
from shared.constants import SERVER_PORT, SERVER_ADDRESS

class NetworkClient():
    ## Server waits for at least 3 clients to connect.
    ## Server starts the game.
    def __init__(self, SERVER_ADDRESS=SERVER_ADDRESS, SERVER_PORT=SERVER_PORT):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((SERVER_ADDRESS, SERVER_PORT))
        self.player_id = None
        self.listeners = []

        threading.Thread(target=self.listen, daemon=True).start()

    def send(self, data: dict):
        ## Send data to the server.
        self.sock.sendall(encode_message(data))

    def listen(self):
        ## Listen for incoming data from the server.
        buffer = b""
        while True:
            try:
                msg = self.sock.recv(4096)
                if not msg:
                    break
                buffer += msg
                from shared.protocol import decode_many
                for message in decode_many(buffer):
                    for callback in self.listeners:
                        callback(message)
                buffer = b""
            except Exception as e:
                print(f"[NETWORK] Error: {e}")
                break

    def get_game_state(self):
        ## Get the current game state from the server.
        pass

    def on_message(self, callback):
        self.listeners.append(callback)