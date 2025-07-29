import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

## Handle network requests
import socket
import threading
from game import Game
from shared.protocol import encode_message, decode_message
from shared.constants import SERVER_PORT, SERVER_ADDRESS

def handle_client(client_socket, game, player_id):
    ## Receive data from the client and update the game state.
    try:
        client_socket.sendall(encode_message({"type": "assign_id", "player_id": player_id}))
    except:
        print(f"[SERVER] Failed to assign player ID to client {player_id}")
        return
    
    while True:
        try:
            message = client_socket.recv(1024)
            if not message:
                break
            data = decode_message(message)
            action = data.get('action')
            game.process_input(player_id, action)
        except Exception as e:
            print(f"[SERVER] Error handling client {player_id}: {e}")
            break

def broadcast(game_state, clients):
    ## Send the current game state to all connected clients.
    encoded = encode_message(game_state)
    for client in clients:
        try:
            client.sendall(encoded)
        except:
            print("[SERVER] Error sending to client")

def wait_for_clients(game):
    ## Wait for clients to connect and start the game.
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((SERVER_ADDRESS, SERVER_PORT))
    server_socket.listen()
    print(f"[SERVER] Listening on port {SERVER_PORT}...")
    
    clients = []
    for i in range(3):
        client_socket, addr = server_socket.accept()
        print(f"[SERVER] Client connected from {addr}")
        clients.append(client_socket)
        player_id = i + 1
        game.players[i].id = player_id
        threading.Thread(
            target=handle_client,
            args=(client_socket, game, player_id),
            daemon=True
        ).start()

    print("[SERVER] Minimum players reached. Starting game.")
    game.start(clients)

if __name__ == "__main__":  ## Main for testing
    game = Game()
    wait_for_clients(game)