## Handle network requests
import socket
import threading
import json
from shared.protocol import encode_message, decode_message
from shared.constants import SERVER_PORT, SERVER_ADDRESS

class NetworkClient():
    ## Server waits for at least 3 clients to connect.
    ## Server starts the game.
    def __init__(self, SERVER_ADDRESS=SERVER_ADDRESS, SERVER_PORT=SERVER_PORT):
        ## Initialize the network client with the server address.
        pass

    def send(self, data: dict):
        ## Send data to the server.
        pass

    def listen(self):
        ## Listen for incoming data from the server.
        pass

    def get_game_state(self):
        ## Get the current game state from the server.
        pass