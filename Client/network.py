## Handle network requests
import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import socket
import threading
from shared.protocol import encode_message, decode_message, decode_many
from shared.constants import SERVER_PORT, SERVER_ADDRESS

class NetworkClient():
    def __init__(self, host=SERVER_ADDRESS, port=SERVER_PORT):
        ## Initialize the network client with the server address.
        ## TODO: Make sure we don't have any unnecessary fields.

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((host, port))
        self.running = True

        ## For fetching game_states one-by-one when multiple messages are received at once.
        self.game_states = {} ## dictionary of game_state dictionaries
        self.listeners = []
        self.count = 0

        threading.Thread(target=self.listen, daemon=True).start()

    def send(self, data: dict):
        ## Send data to the server.
        self.sock.sendall(encode_message(data))

    def listen(self):
        ## Listen for incoming data from the server.
        buffer = b""
        while self.running:
            try:
                msg = self.sock.recv(4096)
                if not msg:
                    self.running = False
                else:
                    buffer += msg
                    game_states = decode_many(buffer)
                    '''
                    for message in game_states:
                        self.count += 1
                        for callback in self.listeners:
                            callback(message)
                    '''
                    buffer = b""
            except Exception as e:
                print(f"[NETWORK] Error: {e}")
                break

    def get_game_state(self):
        ## Get the current game state from the server.
        ## TODO: Dequeue properly.
        if not self.game_states:
            return None
        game_state = self.game_states.pop(0)
        '''
        index = 0
        if index < (self.count - 1):
            game_state = self.game_states[index]
            index += 1
        else:
            game_state = None
        '''
        return game_state
    
    def on_message(self, callback):
        self.listeners.append(callback)
    
    def close(self):
        ## Shut down connection.
        self.running = False
        self.sock.shutdown(socket.SHUT_RDWR)
        self.sock.close()
        self.listener.join()